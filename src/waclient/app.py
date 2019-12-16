# -*- coding: utf-8 -*-
import functools
import logging
import os
import shutil
from os.path import join, dirname
from pathlib import Path

os.environ["KIVY_NO_ARGS"] = "1"

import kivy
kivy.require("1.8.0")

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger as logger
from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.uix.carousel import Carousel
from kivy.uix.filechooser import filesize_units
from kivy.uix.settings import SettingsWithTabbedPanel

from oscpy.server import ServerClass
from waclient.common_config import (
    INTERNAL_CONTAINERS_DIR,
    get_encryption_conf,
    request_multiple_permissions,
    DEFAULT_CONFIG_TEMPLATE,
    APP_CONFIG_FILE,
    request_external_storage_dirs_access,
    SRC_ROOT_DIR)
from waclient.service_controller import ServiceController
from waclient.utilities.logging import CallbackHandler
from waclient.utilities.misc import safe_catch_unhandled_exception
from waclient.utilities.osc import get_osc_server
# from waclient.utilities.i18n import Lang
from wacryptolib.container import (
    extract_metadata_from_container,
    get_encryption_configuration_summary,
)
from wacryptolib.utilities import load_from_json_file




class A:  # TODO put back translation tooling
    def _(self, a):
        return a


tr = A()  # ("en")


osc, osc_starter_callback = get_osc_server(is_master=True)


@ServerClass
class WitnessAngelClientApp(App):
    """
    Main GUI app, which controls the recording service (via OSC protocol), and
    exposes settings as well as existing containers.
    """

    title = "Witness Angel"

    service_querying_interval = 2  # To check when service is ready, at app start

    use_kivy_settings = False  # No need

    language = None

    def __init__(self, **kwargs):
        print("STARTING INIT OF WitnessAngelClientApp")
        super(WitnessAngelClientApp, self).__init__(**kwargs)
        print("AFTER PARENT INIT OF WitnessAngelClientApp")
        self.settings_cls = SettingsWithTabbedPanel
        osc_starter_callback()  # Opens server port
        print("FINISHED INIT OF WitnessAngelClientApp")

    def get_app_icon(self):
        return self.get_asset_abspath("data/icons/witness_angel_logo_256.png")

    def build(self):
        """Initialize the GUI based on the kv file and set up events.

        Returns the root widget of the app.
        """
        self.icon = self.get_app_icon()
        self.language = self.config.getdefault("usersettings", "language", "en")
        # tr.switch_lang(self.language)  TODO LATER

        self._console_output = self.root.ids.kivy_console.console_output
        return self.root

    def load_config(self):
        # We create the initial configuration for the app if it doesn't exist
        config_file = Path(self.get_application_config())
        if not config_file.exists():
            shutil.copy(DEFAULT_CONFIG_TEMPLATE, dst=config_file)
        super().load_config()

    def get_application_config(self, *args, **kwargs):
        return str(APP_CONFIG_FILE)  # IMPORTANT, stringify it for Kivy!

    def build_config(self, config):
        """Create a config file on disk and assign the ConfigParser object to
        `self.config`.
        """
        config.add_section("usersettings")  # Just to please Kivy

    def build_settings(self, settings):
        """Read the user settings schema and create a panel from it."""
        settings_file = join(dirname(__file__), "user_settings_schema.json")
        settings.add_json_panel(
            title=self.title, config=self.config, filename=settings_file
        )

    def on_config_change(self, config, section, key, value):
        """Called when the user changes a config value via the settings panel.
        """
        pass
        """
        if config is self.config:
            token = (section, key)
            if token == ("usersettings", "timer_interval"):
                self.timer_interval = TIMER_OPTIONS[value]
            elif token == ("usersettings", "language"):
                tr.switch_lang(value)
        """

    def on_pause(self):
        """Enables the user to switch to another application, causing the app to wait
        until the user switches back to it eventually.
        """
        return True  # ACCEPT pausing

    def on_resume(self):
        """Called when the app is resumed. Used to restore data that has been
        stored in on_pause().
        """
        pass

    def on_start(self):
        """Event handler for the `on_start` event which is fired after
        initialization (after build() has been called) but before the
        application has started running the events loop.
        """

        self.service_controller = ServiceController()
        self.service_controller.start_service()

        # Redirect root logger traffic to GUI console
        logging.getLogger(None).addHandler(CallbackHandler(self.log_output))

        self.root.ids.recording_btn.disabled = True
        Clock.schedule_interval(
            self._request_recording_state, self.service_querying_interval
        )

        request_multiple_permissions(
            permissions=[
                "WRITE_EXTERNAL_STORAGE",
                "RECORD_AUDIO",
                "CAMERA",
                "ACCESS_FINE_LOCATION",
            ]
        )  # These permissions might NOT be granted by user!

        # import logging_tree
        # logging_tree.printout()

    @property
    def internal_containers_dir(self):
        return str(INTERNAL_CONTAINERS_DIR)

    def get_asset_abspath(self, asset_relpath):
        """Return the absolute path to an asset like "data/icons/myimage.png"."""
        return str(SRC_ROOT_DIR.joinpath(asset_relpath))

    def on_stop(self):
        """Event handler for the `on_stop` event which is fired when the
        application has finished running (i.e. the window is about to be
        closed).
        """
        self.service_controller.stop_service()  # Will wait for termination, else kill it

    def log_output(self, msg, *args, **kwargs):
        """
        Extra args/kwargs are for example the "dt" parameter of Clock callbacks.
        """
        self._console_output.add_text(msg)

    def switch_to_recording_state(self, is_recording):
        self.root.ids.recording_btn.disabled = True
        if is_recording:
            self.service_controller.start_recording()
        else:
            self.service_controller.stop_recording()
        # TODO - schedule here some delayed broadcast_recording_state() calls if OSC is not safe enough

    @osc.address_method("/log_output")
    @safe_catch_unhandled_exception
    def _post_log_output(self, msg):
        callback = functools.partial(self.log_output, msg)
        Clock.schedule_once(callback)

    def _request_recording_state(self, *args, **kwargs):
        """Ask the service for an update on its recording state."""
        self.service_controller.broadcast_recording_state()

    @osc.address_method("/receive_recording_state")
    @safe_catch_unhandled_exception
    def receive_recording_state(self, is_recording):
        # print(">>>>>receive_recording_state", is_recording)
        expected_state = "down" if is_recording else "normal"
        self.root.ids.recording_btn.state = expected_state
        self.root.ids.recording_btn.disabled = False
        Clock.unschedule(self._request_recording_state)

    @staticmethod
    def get_nice_size(size):
        for unit in filesize_units:
            if size < 1024.0:
                return "%1.0f %s" % (size, unit)
            size /= 1024.0
        return size

    def get_container_info(self, filepath):
        """Return a text with info about the container algorithms and inner members metadata.
         """
        if not filepath:
            return "Please select a container"

        filename = os.path.basename(filepath)
        try:
            container = load_from_json_file(filepath)

            info_lines = []

            metadata = extract_metadata_from_container(container)
            if not metadata:
                info_lines.append(
                    "No metadata found in container regarding inner files."
                )

            info_lines.append("MEMBERS:")
            for member_name, member_metadata in sorted(metadata["members"].items()):
                # TODO later add more info
                nice_size = self.get_nice_size(member_metadata["size"])
                info_lines.append("- %s (%s)" % (member_name, nice_size))

            info_lines.append("")

            info_lines.append("ALGORITHMS:")
            summary = get_encryption_configuration_summary(container)
            info_lines.append(summary)

            return "\n".join(info_lines)

        except FileNotFoundError:
            return "This container was deleted"
        except Exception as exc:
            logging.error("Error when reading container %s: %r", filename, exc)
            return "Container analysis failed"

    def purge_all_containers(self):
        """Delete all containers from internal storage."""
        containers_dir = self.internal_containers_dir
        logger.info("Purging all containers from %s", containers_dir)
        for filename in os.listdir(containers_dir):
            filepath = os.path.join(containers_dir, filename)
            os.remove(filepath)
        self.refresh_filebrowser()

    def refresh_filebrowser(self):
        self.root.ids.filebrowser._update_files()
        # TODO: test with latest Kivy, else open ticket regarding this part:
        # "on_entries_cleared: treeview.root.nodes = []" not calling _trigger_layout()
        self.root.ids.filebrowser.layout.ids.treeview._trigger_layout()  # TEMPORARY

    def attempt_container_decryption(self, filepath):
        assert isinstance(filepath, str), filepath
        if not request_external_storage_dirs_access():
            logger.warning("Access to external storage not granted by system yet.")
            return
        self.service_controller.attempt_container_decryption(filepath)

    def get_encryption_conf_text(self):
        """Return the global conf for container encryption."""
        conf = get_encryption_conf()
        return get_encryption_configuration_summary(conf)


def main():
    WitnessAngelClientApp().run()
