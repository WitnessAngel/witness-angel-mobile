# -*- coding: utf-8 -*-
import json
import os, sys
import logging

from kivy.uix.filechooser import filesize_units

from wacryptolib.container import extract_metadata_from_container
from wacryptolib.utilities import load_from_json_file, dump_to_json_str

os.environ["KIVY_NO_ARGS"] = "1"


import functools

import threading
import time
from pathlib import Path

import kivy
from kivy.uix.settings import SettingsWithTabbedPanel
from oscpy.server import OSCThreadServer, ServerClass

from waclient.common_config import INTERNAL_CONTAINERS_DIR, ENCRYPTION_CONF
from waclient.utilities import swallow_exception
from waclient.utilities.i18n import Lang
from waclient.utilities.logging import CallbackHandler
from waclient.utilities.osc import get_osc_server

kivy.require("1.8.0")

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger as logger
from kivy.properties import BoundedNumericProperty, ObjectProperty
from kivy.uix.carousel import Carousel
from os.path import join, dirname
from waclient.service_controller import ServiceController

TIMER_OPTIONS = {
    "1/60 sec": 1 / 60.0,
    "1/30 sec": 1 / 30.0,
    "1/15 sec": 1 / 15.0,
}

tr = Lang("en")


osc, osc_starter_callback = get_osc_server(is_master=True)


@ServerClass
class WitnessAngelClientApp(App):
    """Simple Slideshow App with a user defined title.

    Attributes:
      title (str): Window title of the application

      timer (:class:`kivy.properties.BoundedNumericProperty`):
        Helper for the slide transition of `carousel`

      carousel (:class:`kivy.uix.carousel.Carousel`):
        Widget that holds several slides about the app
    """

    title = "Witness Angel"
    path = []
    timer = BoundedNumericProperty(0, min=0, max=400)
    carousel = ObjectProperty(Carousel)
    language = None
    service_querying_interval = 0.3  # To check when service is ready at start

    use_kivy_settings = False  # TODO disable this in prod

    _sock = None

    def __init__(self, **kwargs):
        super(WitnessAngelClientApp, self).__init__(**kwargs)
        self.settings_cls = SettingsWithTabbedPanel

    def start_timer(self, *args, **kwargs):
        """Schedule the timer update routine and fade in the progress bar."""
        logger.debug("Starting timer")
        Clock.schedule_interval(self._update_timer, self.timer_interval)
        self.progress_bar.fade_in()

    def stop_timer(self, *args, **kwargs):
        """Reset the timer and unschedule the update routine."""
        logger.debug("Stopping timer")
        Clock.unschedule(self._update_timer)
        self.progress_bar.fade_out()
        self.timer = 0

    def delay_timer(self, *args, **kwargs):
        """Stop the timer but re-schedule it based on `anim_move_duration` of
        :attr:`WitnessAngelClientApp.carousel`.
        """
        self.stop_timer()
        Clock.schedule_once(self.start_timer, self.carousel.anim_move_duration)

    def build(self):
        """Initialize the GUI based on the kv file and set up events.

        Returns:
          (:class:`kivy.uix.anchorlayout.AnchorLayout`): Root widget specified
            in the kv file of the app
        """
        # print ("CONFIG IS", self.config)
        self.language = self.config.get("usersettings", "language")
        tr.switch_lang(self.language)

        #user_interval = self.config.get("usersettings", "timer_interval")
        #self.timer_interval = TIMER_OPTIONS[user_interval]

        self.carousel = self.root.ids.carousel
        self.progress_bar = self.root.ids.progress_bar
        self.progress_bar.max = self.property("timer").get_max(self)

        """
        self.start_timer()
        self.carousel.bind(on_touch_down=self.stop_timer)
        self.carousel.bind(current_slide=self.delay_timer)
        """

        self._console_output = self.root.ids.kivy_console.console_output
        return self.root

    def build_config(self, config):
        """Create a config file on disk and assign the ConfigParser object to
        `self.config`.
        """
        config.add_section("usersettings")
        """
        config.setdefaults(
                section="usersettings", keyvalues={"timer_interval": "1/60 sec", "language": "en"}
        )
        """

    def build_settings(self, settings):
        """Read the user settings and create a panel from it."""
        settings_file = join(dirname(__file__), "user_settings_schema.json")
        settings.add_json_panel(
                title=self.title, config=self.config, filename=settings_file
        )

    def on_config_change(self, config, section, key, value):
        """Called when the user changes the config values via the settings
        panel. If `timer_interval` is being changed update the instance
        variable of the same name accordingly.
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
        """Enables the user to switch to another application causing
        :class:`WitnessAngelClientApp` to wait until the user
        switches back to it eventually.
        """
        return True

    def on_resume(self):
        """Called when the app is resumed. Used to restore data that has been
        stored in :meth:`WitnessAngelClientApp.on_pause`.
        """
        pass

    def on_start(self):
        '''Event handler for the `on_start` event which is fired after
        initialization (after build() has been called) but before the
        application has started running.
        '''
        osc_starter_callback()  # Opens server port

        self.service_controller = ServiceController()
        self.service_controller.start_service()

        # Push root logger traffic to GUI console
        logging.getLogger(None).addHandler(CallbackHandler(self.log_output))

        self.root.ids.recording_btn.disabled = True
        Clock.schedule_interval(self._request_recording_state, self.service_querying_interval)

        #import logging_tree
        #logging_tree.printout()

    def on_stop(self):
        '''Event handler for the `on_stop` event which is fired when the
        application has finished running (i.e. the window is about to be
        closed).
        '''
        self.service_controller.stop_service()  # Will wait for termination else kill

    def _update_timer(self, dt):
        try:
            self.timer += 1
        except ValueError:
            self.stop_timer()
            self.carousel.load_next()
            logger.debug("Automatically loading next slide")

    def log_output(self, msg, *args, **kwargs):
        """
        Extra args/kwargs are for example the "dt" parameter of Clock callbacks.
        """
        self._console_output.add_text(msg)

    def switch_to_recording_state(self, is_recording):
        #print(">--->>switch_to_recording_state", is_recording)
        self.root.ids.recording_btn.disabled = True
        if is_recording:
            self.service_controller.start_recording()
        else:
            self.service_controller.stop_recording()
        # TODO - schedule here broadcast_recording_state() calls if OSC is not safe enough..

    @osc.address_method('/log_output')
    @swallow_exception
    def _post_log_output(self, msg):
        callback = functools.partial(self.log_output, msg)
        Clock.schedule_once(callback)

    def _request_recording_state(self, *args, **kwargs):
        self.service_controller.broadcast_recording_state()

    @osc.address_method('/receive_recording_state')
    @swallow_exception
    def receive_recording_state(self, is_recording):
        #print(">>>>>receive_recording_state", is_recording)
        expected_state = "down" if is_recording else "normal"
        self.root.ids.recording_btn.state = expected_state
        self.root.ids.recording_btn.disabled = False
        Clock.unschedule(self._request_recording_state)

    #def get_path(self, sd_path):
     #   """Called when a file is selected in the File Chooser Widget."""
     #   print(Path(__file__).parents[2] / "data")
     #   self.path = sd_path

    @staticmethod
    def get_nice_size(size):
        for unit in filesize_units:
            if size < 1024.0:
                return '%1.0f %s' % (size, unit)
            size /= 1024.0
        return size

    def get_container_info(self, filepath):
        """Just a test of the path usability of the
         widget FileChooserListView
         """
        #print("-----> STATING", filepath)
        if not filepath:
            return "Please select a container"
        filename = os.path.basename(filepath)
        try:
            container = load_from_json_file(filepath)
            metadata = extract_metadata_from_container(container)
            if not metadata:
                return "No metadata found in container"
            info_lines = ["MEMBERS:"]
            for member_name, member_metadata in sorted(metadata["members"].items()):
                #TODO later add more info
                nice_size = self.get_nice_size(member_metadata["size"])
                info_lines.append("- %s (%s)" % (member_name, nice_size))
            return "\n".join(info_lines)
            #return str(os.stat(filepath).st_size)
        except FileNotFoundError:
            return "This container was deleted"
        except Exception as exc:
            logging.error("Error when reading container %s: %r", filename, exc)
            return "Container analysis failed"

    def purge_all_containers(self):
        containers_dir = self.internal_containers_dir()
        logger.info("Purging all containers from %s", containers_dir)
        for filename in os.listdir(self.internal_containers_dir()):
            filepath = os.path.join(containers_dir, filename)
            os.remove(filepath)
        self.refresh_filebrowser()

    def refresh_filebrowser(self):
        #self.root.ids.filebrowser.files = []
        self.root.ids.filebrowser._update_files()  # _trigger_update()
        #if not self.root.ids.filebrowser.files:
        #    self.root.ids.filebrowser.on_entries_cleared() # canvas.ask_update()

        # TODO: test with latest Kivy, else open ticket regarding this part:
        # "on_entries_cleared: treeview.root.nodes = []" not calling _trigger_layout()
        self.root.ids.filebrowser.layout.ids.treeview._trigger_layout()  # TEMPORARY

    def internal_containers_dir(self):
        return str(INTERNAL_CONTAINERS_DIR)

    def get_encryption_conf_text(self):
        return dump_to_json_str(ENCRYPTION_CONF, indent=2)
