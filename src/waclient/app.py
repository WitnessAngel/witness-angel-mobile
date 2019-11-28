# -*- coding: utf-8 -*-

import os
from pathlib import Path

import kivy
from kivy.uix.settings import SettingsWithTabbedPanel

from waclient.utilities.i18n import Lang

kivy.require("1.8.0")

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
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

    use_kivy_settings = True  # TODO disable this in prod

    def __init__(self, **kwargs):
        super(WitnessAngelClientApp, self).__init__(**kwargs)
        self.settings_cls = SettingsWithTabbedPanel
        self.service_controller = ServiceController()
        self.service_controller.start_service()

    def start_timer(self, *args, **kwargs):
        """Schedule the timer update routine and fade in the progress bar."""
        Logger.debug("Starting timer")
        Clock.schedule_interval(self._update_timer, self.timer_interval)
        self.progress_bar.fade_in()

    def stop_timer(self, *args, **kwargs):
        """Reset the timer and unschedule the update routine."""
        Logger.debug("Stopping timer")
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

        user_interval = self.config.get("usersettings", "timer_interval")
        self.timer_interval = TIMER_OPTIONS[user_interval]

        self.carousel = self.root.ids.carousel
        self.progress_bar = self.root.ids.progress_bar
        self.progress_bar.max = self.property("timer").get_max(self)

        self.start_timer()
        self.carousel.bind(on_touch_down=self.stop_timer)
        self.carousel.bind(current_slide=self.delay_timer)
        return self.root

    def build_config(self, config):
        """Create a config file on disk and assign the ConfigParser object to
        `self.config`.
        """
        config.setdefaults(
                section="usersettings", keyvalues={"timer_interval": "1/60 sec", "language": "en"}
        )

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
        if config is self.config:
            token = (section, key)
            if token == ("usersettings", "timer_interval"):
                self.timer_interval = TIMER_OPTIONS[value]
            elif token == ("usersettings", "language"):
                tr.switch_lang(value)

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
        pass

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
            Logger.debug("Automatically loading next slide")

    def log_output(self, msg):
        print(">>>>>>ROOT IDS:", self.root.ids)

        self.root.ids.kivy_console.console_output.add_text(msg)

    def get_path(self, sd_path):
        """Called when a file is selected in the File Chooser Widget."""
        print(Path(__file__).parents[2] / "data")
        self.path = sd_path

    def get_stat(self):
        """Just a test of the path usability of the
         widget FileChooserListView
         """
        return os.stat(self.path)

    def init_dir(self):
        return str(Path(__file__).parents[2] / "tests")
