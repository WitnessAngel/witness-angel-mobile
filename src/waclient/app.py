# -*- coding: utf-8 -*-

import logging
import os

from kivy.logger import Logger as logger

from waguilib.application import WAGuiApp
from wacryptolib.cryptainer import (
    extract_metadata_from_container,
    get_cryptoconf_summary,
)
from wacryptolib.utilities import load_from_json_file

from waclient.common_config import (
    INTERNAL_CONTAINERS_DIR,
    get_cryptoconf,
    request_multiple_permissions,
    request_external_storage_dirs_access,
    SRC_ROOT_DIR,
    DEFAULT_REQUESTED_PERMISSIONS_MAPPER,
    request_single_permission, DEFAULT_CONFIG_SCHEMA, APP_CONFIG_FILE, DEFAULT_CONFIG_TEMPLATE)
# from waclient.utilities.i18n import Lang
from waguilib.importable_settings import WIP_RECORDING_MARKER


class A:  # TODO put back translation tooling
    def _(self, a):
        return a


tr = A()  # ("en")



class WitnessAngelClientApp(WAGuiApp):

    # CLASS VARIABLES #
    title = "Witness Angel"
    app_config_file = str(APP_CONFIG_FILE)
    default_config_template = str(DEFAULT_CONFIG_TEMPLATE)
    default_config_schema = str(DEFAULT_CONFIG_SCHEMA)
    wip_recording_marker = str(WIP_RECORDING_MARKER)


    def get_app_icon(self):
        return self.get_asset_abspath("data/icons/witness_angel_logo_256.png")

    def build(self):
        """Initialize the GUI based on the kv file and set up events.

        Returns the root widget of the app.
        """
        super().build()
        self.icon = self.get_app_icon()
        self.language = self.config.getdefault("usersettings", "language", "en")
        # tr.switch_lang(self.language)  TODO LATER

        self._console_output = self.root.ids.kivy_console.console_output

    def on_config_change(self, config, section, key, value):
        """Called when the user changes a config value via the settings panel."""
        if config is self.config:
            token = (section, key)
            if token == ("usersettings", "daemonize_service"):
                self.switch_daemonize_service(int(value))  # Passed as STR!!
            elif key in DEFAULT_REQUESTED_PERMISSIONS_MAPPER and int(value):
                logger.info("on_config_change %s %s", key, value)
                request_single_permission(DEFAULT_REQUESTED_PERMISSIONS_MAPPER[key])

    def on_start(self):
        """Event handler for the `on_start` event which is fired after
        initialization (after build() has been called) but before the
        application has started running the events loop.
        """
        super().on_start()
        # These permissions might NOT be granted now by user!
        self._request_permissions_for_all_enabled_sensors()

    def _request_permissions_for_all_enabled_sensors(self, only_this_sensor=None):
        """"
        Loop on user settinsg, and only request permissions for enabled sensors.
        """
        needed_permissions = []
        for (setting, permission) in DEFAULT_REQUESTED_PERMISSIONS_MAPPER.items():
            if self.config.getboolean("usersettings", setting):
                needed_permissions.append(permission)
        if needed_permissions:
            logger.info("Checking necessary user permissions %s" % str(needed_permissions))
            request_multiple_permissions(
                permissions=needed_permissions
            )

    def get_daemonize_service(self):
        return self.config.getboolean("usersettings", "daemonize_service")

    @property
    def internal_containers_dir(self):
        return str(INTERNAL_CONTAINERS_DIR)

    def get_asset_abspath(self, asset_relpath):
        """Return the absolute path to an asset like "data/icons/myimage.png"."""
        return str(SRC_ROOT_DIR.joinpath(asset_relpath))

    def log_output(self, msg, *args, **kwargs):
        """
        Extra args/kwargs are for example the "dt" parameter of Clock callbacks.
        """
        self._console_output.add_text(msg)

    def get_container_info(self, filepath):  # FIXME centralize this
        """Return a text with info about the container algorithms and inner members metadata.
         """
        if not filepath:
            return "Please select a container"

        filename = os.path.basename(filepath)
        try:
            container = load_from_json_file(filepath)  # FIXME use dedicated wacryptolib methods

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

            info_lines.append("KEYCHAIN ID:")
            info_lines.append(str(container.get("keychain_uid", "<not found>")))

            info_lines.append("")

            info_lines.append("ALGORITHMS:")
            summary = get_cryptoconf_summary(container)
            info_lines.append(summary)

            return "\n".join(info_lines)

        except FileNotFoundError:
            return "This container was deleted"
        except Exception as exc:
            logging.error("Error when reading container %s: %r", filename, exc)
            return "Container analysis failed"

    def purge_all_containers(self):  # FIXME use wacryptolib methods!
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
        assert isinstance(filepath, str), filepath  # OSCP doesn't handle Path instances
        if not request_external_storage_dirs_access():
            logger.warning("Access to external storage not granted, aborting decryption attempt.")
            return
        self.service_controller.attempt_container_decryption(filepath)

    def get_cryptoconf_text(self):
        """Return the globalcryptoconffor container encryption."""
       cryptoconf= get_cryptoconf()
        return get_cryptoconf_summary(conf)


def main():
    WitnessAngelClientApp().run()
