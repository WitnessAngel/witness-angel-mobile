from kivy.app import App
from kivy.base import runTouchApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, ListProperty, StringProperty, \
    NumericProperty, Clock, partial
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
import os
import sys


Builder.load_string('''
<KivyConsole>:
    console_output: console_output
    scroll_view: scroll_view
    ScrollView:
        id: scroll_view
        bar_width: 10
        ConsoleOutput:
            id: console_output
            readonly: True
            padding: 6, 6
            size_hint: (1, None)
            font_name: root.font_name
            font_size: root.font_size
            foreground_color: root.foreground_color
            background_color: root.background_color
            height: max(self.parent.height, self.minimum_height)
''')


class ConsoleOutput(TextInput):

    #__events__ = ('on_start', )

    def __init__(self, **kwargs):
        super(ConsoleOutput, self).__init__(**kwargs)
        app = App.get_running_app()
        app.bind(on_start=self.my_on_start)


    def is_at_bottom(self):
        return (self.parent.scroll_y <= 0.05)

    def scroll_to_bottom(self):
        self.parent.scroll_y = 0

    def add_text(self, text):
        is_locked = self.is_at_bottom()
        self.text += text
        self.parent.scroll_y = 0
        if is_locked:
            #print("FORCE SCROLL", self.parent.scroll_y)
            #self.parent.scroll_y = 1  # lock-to-bottom behaviour
        ##print(output)
        #Clock.schedule_once(self.parent.scroll_y = 1)

    def my_on_start(self, *args, **kwargs):
        print(">MY ON START", args, kwargs, self.parent)
        self.add_text("\n".join(str(i) for i in range(50)))

class KivyConsole(BoxLayout):

    console_output = ObjectProperty(None)
    '''Instance of ConsoleOutput
       :data:`console_output` is an :class:`~kivy.properties.ObjectProperty`
    '''

    scroll_view = ObjectProperty(None)
    '''Instance of :class:`~kivy.uix.scrollview.ScrollView`
       :data:`scroll_view` is an :class:`~kivy.properties.ObjectProperty`
    '''

    foreground_color = ListProperty((1, 1, 1, 1))
    '''This defines the color of the text in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(.5, .5, .5, .93)'
    '''

    background_color = ListProperty((0, 0, 0, 1))
    '''This defines the color of the background in the console

    :data:`foreground_color` is an :class:`~kivy.properties.ListProperty`,
    Default to '(0, 0, 0, 1)'''

    font_name = StringProperty('data/fonts/Roboto-Regular.ttf')
    '''Indicates the font Style used in the console

    :data:`font` is a :class:`~kivy.properties.StringProperty`,
    Default to 'DroidSansMono'
    '''

    font_size = NumericProperty(14)
    '''Indicates the size of the font used for the console

    :data:`font_size` is a :class:`~kivy.properties.NumericProperty`,
    Default to '9'
    '''

    def __init__(self, **kwargs):
        super(KivyConsole, self).__init__(**kwargs)



if __name__ == '__main__':
    runTouchApp(KivyConsole())
