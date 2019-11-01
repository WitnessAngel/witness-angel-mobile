# -*- coding: utf-8 -*-

import webbrowser
import gettext
import sys
from pathlib import Path
import os

import kivy
from kivy.uix.settings import SettingsWithTabbedPanel

kivy.require('1.8.0')

from kivy.lang import Observable
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.properties import (
    BoundedNumericProperty, ObjectProperty, StringProperty
)
from kivy.uix.carousel import Carousel
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from os.path import join, dirname

TIMER_OPTIONS = {
    '1/60 sec': 1 / 60.0,
    '1/30 sec': 1 / 30.0,
    '1/15 sec': 1 / 15.0,
}

LOCALE_DIR = (Path(__file__).parents[2] / "data" / "locales")
print("LOCALE DIR", LOCALE_DIR)



class RefLabel(Label):
    """Simple that opens a contained url in the webbrowser."""

    def on_ref_press(self, url):
        """Callback which is being run when the user clicks on a ref in the
        label.

        :param str url: URL to be opened in the webbrowser
        """
        Logger.info("Opening '{url}' in webbrowser.".format(url=url))
        webbrowser.open(url)


class TransitionProgress(ProgressBar):
    """ProgressBar with pre-defined animations for fading in and out."""

    _in = Animation(opacity=1.0, duration=0.4)
    _out = Animation(opacity=0.0, duration=0.1)

    def fade_in(self):
        """Play the animation for changing the ProgressBar to be opaque."""
        self._in.start(self)

    def fade_out(self):
        """Play the animation to hide the ProgressBar."""
        self._out.start(self)


class Lang(Observable):
    """Internationalization of the program : https://github.com/tito/kivy-gettext-example"""
    observers = []
    lang = None

    def __init__(self, defaultlang):
        super(Lang, self).__init__()
        self.ugettext = None
        self.lang = defaultlang
        self.switch_lang(self.lang)

    def _(self, text):
        return self.ugettext(text)

    def fbind(self, name, func, args, **kwargs):
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            return super(Lang, self).fbind(name, func, *largs, **kwargs)

    def funbind(self, name, func, args, **kwargs):
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            return super(Lang, self).funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        # instanciate a gettext
        locales = gettext.translation(
            'witness-angel-client', LOCALE_DIR, languages=[lang])
        self.ugettext = locales.gettext

        # update all the kv rules attached to this text
        for func, largs, kwargs in self.observers:
            func(largs, None, None)

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

    title = 'Witness Angel'
    path = []
    timer = BoundedNumericProperty(0, min=0, max=400)
    carousel = ObjectProperty(Carousel)

    use_kivy_settings = True  # TODO disable this in prod

    def __init__(self, language, **kwargs):
        super(WitnessAngelClientApp, self).__init__(**kwargs)
        self.language = language
        #self.switch_lang(self.language)
        self.settings_cls = SettingsWithTabbedPanel

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
        Clock.schedule_once(
            self.start_timer,
            self.carousel.anim_move_duration
        )

    def build(self):
        """Initialize the GUI based on the kv file and set up events.

        Returns:
          (:class:`kivy.uix.anchorlayout.AnchorLayout`): Root widget specified
            in the kv file of the app
        """
        #print ("CONFIG IS", self.config)
        self.language = self.config.get('usersettings', 'language')
        tr.switch_lang(self.language)

        user_interval = self.config.get('usersettings', 'timer_interval')
        self.timer_interval = TIMER_OPTIONS[user_interval]

        self.carousel = self.root.ids.carousel
        self.progress_bar = self.root.ids.progress_bar
        self.progress_bar.max = self.property('timer').get_max(self)

        self.start_timer()
        self.carousel.bind(on_touch_down=self.stop_timer)
        self.carousel.bind(current_slide=self.delay_timer)
        return self.root

    def build_config(self, config):
        """Create a config file on disk and assign the ConfigParser object to
        `self.config`.
        """
        config.setdefaults(
            'usersettings', {
                'timer_interval': '1/60 sec',
                'language': 'en'
            }
        )

    def build_settings(self, settings):
        """Read the user settings and create a panel from it."""
        settings_file =  join(dirname(__file__), 'usersettings.json')
        settings.add_json_panel(title=self.title, config=self.config, filename=settings_file)

    def on_config_change(self, config, section, key, value):
        """Called when the user changes the config values via the settings
        panel. If `timer_interval` is being changed update the instance
        variable of the same name accordingly.
        """
        if config is self.config:
            token = (section, key)
            if token == ('usersettings', 'timer_interval'):
                self.timer_interval=TIMER_OPTIONS[value]
            elif token == ('usersettings', 'language'):
                tr.switch_lang(value)

    #def on_start(self):
    #    BBBBBBBBBB

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

    def _update_timer(self, dt):
        try:
            self.timer += 1
        except ValueError:
            self.stop_timer()
            self.carousel.load_next()
            Logger.debug("Automatically loading next slide")


    def log_output(self, msg):
        print (">>>>>>ROOT IDS:", self.root.ids)

        self.root.ids.kivy_console.console_output.add_text(msg)

    def get_path(self,sd_path):
        """Called when a file is selected in the File Chooser Widget."""
        self.path = sd_path

    def get_stat(self):
        """Just a test of the path usability of the
         widget FileChooserListView
         """
        return os.stat(self.path)
