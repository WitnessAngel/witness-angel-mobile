import importlib

from plyer import gyroscope
from plyer.utils import platform

from wacryptolib.sensor import JsonDataAggregator, PeriodicValuePoller

try:
    importlib.import_module('plyer.platforms.{}.{}'.format(platform, "gyroscope"))
    gyroscope_is_implemented = True
except ImportError:
    gyroscope_is_implemented = False

def get_periodic_value_provider(json_aggregator, polling_interval_s):

    def get_gyroscope_rotation():
        rotation_rate = None
        if gyroscope_is_implemented:
            try:
                rotation_rate = gyroscope.rotation
            except NotImplementedError:
                pass  # TODO logging or warnings here?
        if rotation_rate is None:
            rotation_rate = (None, None, None)

        rotation_dict = {"rotation_rate_x": rotation_rate[0],
                         "rotation_rate_y": rotation_rate[1],
                         "rotation_rate_z": rotation_rate[2]}
        print("> got rotation rate", rotation_dict)
        return rotation_dict

    poller = PeriodicValuePoller(
        interval_s=polling_interval_s, task_func=get_gyroscope_rotation, json_aggregator=json_aggregator)

    return poller
