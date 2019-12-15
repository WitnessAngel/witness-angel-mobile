import importlib
import threading

from plyer import gyroscope
from plyer.utils import platform

from wacryptolib.sensor import PeriodicValuePoller
from wacryptolib.utilities import synchronized

try:
    importlib.import_module("plyer.platforms.{}.{}".format(platform, "gyroscope"))
    gyroscope_is_implemented = True
except ImportError:
    gyroscope_is_implemented = False


# print(">>>>>>>>>>>>>>>>>>>>gyroscope_is_implemented", gyroscope_is_implemented)


class GyroscopeValueProvider(PeriodicValuePoller):

    _gyroscope_is_enabled = False
    _lock = threading.Lock()

    @synchronized
    def start(self):
        super().start()
        if gyroscope_is_implemented:
            gyroscope.enable()
        self._gyroscope_is_enabled = True

    @synchronized
    def stop(self):
        super().stop()
        if gyroscope_is_implemented:
            gyroscope.disable()
        self._gyroscope_is_enabled = False

    @synchronized
    def _task_func(self):
        if not self.is_running:
            return  # End of recording
        assert self._gyroscope_is_enabled  # Sanity check for desktop platform

        if gyroscope_is_implemented:
            rotation_rate = gyroscope.rotation
        else:
            rotation_rate = (None, None, None)  # Fake values

        rotation_dict = {
            "rotation_rate_x": rotation_rate[0],
            "rotation_rate_y": rotation_rate[1],
            "rotation_rate_z": rotation_rate[2],
        }
        # print("> got rotation rate", rotation_dict)
        return rotation_dict


def get_gyroscope_sensor(json_aggregator, polling_interval_s):
    sensor = GyroscopeValueProvider(
        interval_s=polling_interval_s, json_aggregator=json_aggregator
    )
    return sensor
