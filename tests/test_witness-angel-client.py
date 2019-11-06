# -*- coding: utf-8 -*-

import gevent
from gevent import monkey

monkey.patch_all()


import time
import unittest
from functools import partial

from kivy.base import EventLoop, runTouchApp
from kivy.clock import Clock

from waclient.waclient_app import WitnessAngelClientApp


class Test(unittest.TestCase):
    # sleep function that catches ``dt`` from Clock
    def pause(*args):
        print("-", end="")
        time.sleep(0.01)

    # main test function
    def run_test(self, app, *args):
        # app.title == 'Witness Angel Client'
        # time.sleep(2)
        print(".")
        if False:
            print("<<<<<<<", app.carousel.slides)
            names = [slide.name for slide in app.carousel.slides]
            expected = ["hello", "kivy", "cookiecutterdozer", "license", "github"]
            assert names == expected

        print("IN RUNTESTS")
        Clock.schedule_interval(self.pause, 0.01)
        print("IN RUNTESTS2")
        time.sleep(2)
        print("IN RUNTESTS3")
        time.sleep(2)
        # Do something

        # Comment out if you are editing the test, it'll leave the
        # Window opened.
        app.stop()

    # same named function as the filename(!)
    def test_example(self):
        app = WitnessAngelClientApp(language="en")
        p = partial(self.run_test, app)
        Clock.schedule_once(self.pause)
        # gevent.spawn(p)
        # app.run()
        greenlet = gevent.spawn(app.run)
        print(">>>>>>>>>>>")
        p()
        gevent.wait([greenlet])
        print("<<<<<<<<<<<<<<<<")


def ___test_slave_app():
    app = WitnessAngelClientApp(language="en")
    app.run(slave=True)
    print(">>>>>>", EventLoop.window)
    runTouchApp()
    # for i in range(100000):
    #     EventLoop.idle()
    # time.sleep(0.001)
    app.stop()


def ___test_app_title(app):
    """Simply tests if the default app title meets the expectations.
itness-angel-client
    Args:
      app (:class:`WitnessAngelClientApp`): Default app instance

    Raises:
      AssertionError: If the title does not match
    """
    assert app.title == "Witness Angel Client"


def ___test_carousel(app):
    """Test for the carousel widget of the app checking the slides' names.

    Args:
      app (:class:`WitnessAngelClientApp`): Default app instance

    Raises:
      AssertionError: If the names of the slides do not match the expectations
    """
    names = [slide.name for slide in app.carousel.slides]
    expected = ["hello", "kivy", "cookiecutterdozer", "license", "github"]
    assert names == expected


if __name__ == "__main__":
    t = Test()
    t.test_example()
