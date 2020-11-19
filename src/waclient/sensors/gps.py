import importlib
import threading

from plyer import gps
from plyer.utils import platform

from wacryptolib.sensor import (
    PeriodicValueMixin,
)
from wacryptolib.utilities import TaskRunnerStateMachineBase, synchronized

try:
    importlib.import_module("plyer.platforms.{}.{}".format(platform, "gps"))
    gps_is_implemented = True
except ImportError:
    gps_is_implemented = False


class GpsValueProvider(PeriodicValueMixin, TaskRunnerStateMachineBase):

    _lock = threading.RLock()  # Recursive due to PC testcase...

    def __init__(self, interval_s: float, **kwargs):
        super().__init__(**kwargs)
        self._interval_s = interval_s
        if gps_is_implemented:
            try:
                gps.configure(on_location=self._on_location, on_status=self._on_status)
            except Exception:
                import traceback

                traceback.print_exc()
                raise

    @synchronized
    def _on_location(self, **kwargs):
        """Called by GPS thread, multiples keys/value are provided
        (typically: lon, lat, speed, bearing, altitude, and accuracy)
        """
        if self.is_running:  # Else, its' a final call after a st_nominal_recording_toolchain_caseop()?
            self._offloaded_add_data(data_dict=kwargs)

    @synchronized
    def _on_status(self, message_type, status):
        """Called by GPS thread, "message_type" and "status" parameters are provided.

        Examples of message_type: "provider-enabled", "provider-disabled", "provider-status"
        (the latter having a status formatted as "provider: substatus".
        """
        if self.is_running:  # Else, its' a final call after a stop()?
            self._offloaded_add_data(data_dict=dict(message_type=message_type, status=status))

    @synchronized
    def start(self):
        super().start()
        if gps_is_implemented:
            gps.start(
                minTime=self._interval_s * 1000,  # In milliseconds (float)
                minDistance=1,
            )  # In meters (float)
        else:
            # Simulate a single push of GPS data
            self._on_location(altitude=2.2)
            self._on_status("some_message_type", "some_status_value")

    @synchronized
    def stop(self):
        super().stop()
        if gps_is_implemented:
            gps.stop()


def get_gps_sensor(json_aggregator, polling_interval_s):
    sensor = GpsValueProvider(
        interval_s=polling_interval_s, json_aggregator=json_aggregator
    )
    return sensor
