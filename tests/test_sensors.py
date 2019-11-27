import time

from wacryptolib.sensor import TarfileAggregator, JsonAggregator
from wacryptolib.utilities import load_from_json_bytes


class FakeTarfileAggregator(TarfileAggregator):

    def __init__(self):
        self._test_records = []

    def add_record(self, **kwargs):
        print("FakeTarfileAggregator->add_record()")
        self._test_records.append(kwargs)

    def finalize_tarfile(self):
        print("FakeTarfileAggregator->finalize_tarfile()")
        self._test_records = []


def test_gyroscope():

    from waclient.sensors.gyroscope import get_periodic_value_provider

    fake_tarfile_aggregator = FakeTarfileAggregator()

    json_aggregator = JsonAggregator(
        max_duration_s=0.5,
        tarfile_aggregator=fake_tarfile_aggregator,
        sensor_name="test_gyroscope",
    )

    sensor = get_periodic_value_provider(json_aggregator=json_aggregator, default_poll_interval_s=0.1)

    sensor.start()

    time.sleep(0.9)

    sensor.stop()
    sensor.join()

    json_aggregator.flush_dataset()
    assert not json_aggregator._current_dataset

    assert len(fake_tarfile_aggregator._test_records) == 2

    print("TEST RECORDS:", fake_tarfile_aggregator._test_records)

    for record in fake_tarfile_aggregator._test_records:
        sensor_entries = load_from_json_bytes(record["data"])
        assert len(sensor_entries) >= 3
        for sensor_entry in sensor_entries:
            assert "rotation_x" in sensor_entry, sensor_entry
            assert "rotation_y" in sensor_entry, sensor_entry
            assert "rotation_z" in sensor_entry, sensor_entry

