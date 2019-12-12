import importlib

from plyer import gps
from plyer.utils import platform

from wacryptolib.sensor import JsonDataAggregator, PeriodicValuePoller, PeriodicValueMixin
from wacryptolib.utilities import TaskRunnerStateMachineBase

from kivy.logger import Logger as logger

try:
    importlib.import_module('plyer.platforms.{}.{}'.format(platform, "gps"))
    gps_is_implemented = True
except ImportError:
    gps_is_implemented = False


print(">>>>>>>>>>gps_is_implemented", gps_is_implemented)


class GpsValueProvider(PeriodicValueMixin, TaskRunnerStateMachineBase):

    def __init__(self, interval_s: int, **kwargs):
        super().__init__(**kwargs)
        self._interval_s = interval_s
        if gps_is_implemented:
            gps.configure(on_location=self._on_location, on_status=self._on_status)

    def _on_location(self, *args, **kwargs):
        logger.info(">>>>>>>> ON LOCATION", args, kwargs)

    def _on_status(self, *args, **kwargs):
        logger.info(">>>>>>>> ON STATUS", args, kwargs)

    def start(self):
        super().start()
        if gps_is_implemented:
            gps.start(minTime=self._interval_s * 1000,  # In milliseconds (float)
                      minDistance=1)  # In meters (float)
        else:
            # Simulate a single push of GPS data
            self._offloaded_add_data(dict(x=66))

    def stop(self):
        super().start()
        if gps_is_implemented:
            gps.stop()


def get_periodic_value_provider(json_aggregator, polling_interval_s):
    poller = GpsValueProvider(interval_s=polling_interval_s, json_aggregator=json_aggregator)
    return poller
