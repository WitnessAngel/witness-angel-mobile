# -*- coding: utf-8 -*-

import webbrowser

from kivy.animation import Animation
from kivy.app import App
from kivy.base import runTouchApp
from kivy.logger import Logger
from kivy.properties import (
    ObjectProperty,
    ListProperty,
    StringProperty,
    NumericProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.textinput import TextInput


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


class ConsoleOutput(TextInput):

    # __events__ = ('on_start', )

    def __init__(self, **kwargs):
        super(ConsoleOutput, self).__init__(**kwargs)
        app = App.get_running_app()
        app.bind(on_start=self.my_on_start)

    def is_at_bottom(self):
        return self.parent.scroll_y <= 0.05

    def scroll_to_bottom(self):
        self.parent.scroll_y = 0

    def add_text(self, text):
        text += "\n"
        is_locked = self.is_at_bottom()
        self.text += text
        self.parent.scroll_y = 0
        if is_locked:
            self.scroll_to_bottom()
            # print("FORCE SCROLL", self.parent.scroll_y)
            # self.parent.scroll_y = 1  # lock-to-bottom behaviour
        ##print(output)
        # Clock.schedule_once(self.parent.scroll_y = 1)

    def my_on_start(self, *args, **kwargs):
        print(">MY ON START", args, kwargs, self.parent)
        self.add_text("\n".join(str(i) for i in range(50)))


class KivyConsole(BoxLayout):
    console_output = ObjectProperty(None)
    """Instance of ConsoleOutput
       :data:`console_output` is an :class:`~kivy.properties.ObjectProperty`
    """

    scroll_view = ObjectProperty(None)
    """Instance of :class:`~kivy.uix.scrollview.ScrollView`
       :data:`scroll_view` is an :class:`~kivy.properties.ObjectProperty`
    """

    foreground_color = ListProperty((1, 1, 1, 1))
    """This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(.5, .5, .5, .93)'
    """

    background_color = ListProperty((0, 0, 0, 1))
    """This defines the color of the background in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(0, 0, 0, 1)"""

    font_name = StringProperty("data/fonts/Roboto-Regular.ttf")
    """Indicates the font Style used in the console

    :data:`font` is a :class:`~kivy.properties.StringProperty`,
    Default to 'DroidSansMono'
    """

    font_size = NumericProperty(14)
    """Indicates the size of the font used for the console

    :data:`font_size` is a :class:`~kivy.properties.NumericProperty`,
    Default to '9'
    """

    def __init__(self, **kwargs):
        super(KivyConsole, self).__init__(**kwargs)


if __name__ == "__main__":
    runTouchApp(KivyConsole())
