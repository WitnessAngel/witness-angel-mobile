import time

from wacryptolib.sensor import TarfileRecordsAggregator, JsonDataAggregator
from wacryptolib.utilities import load_from_json_bytes


class FakeTarfileRecordsAggregator(TarfileRecordsAggregator):
    def __init__(self):
        self._test_records = []

    def add_record(self, **kwargs):
        print("FakeTarfileRecordsAggregator->add_record()")
        self._test_records.append(kwargs)

    def finalize_tarfile(self):
        print("FakeTarfileRecordsAggregator->finalize_tarfile()")
        self._test_records = []


def test_gyroscope_sensor():

    from waclient.sensors.gyroscope import get_gyroscope_sensor

    fake_tarfile_aggregator = FakeTarfileRecordsAggregator()

    json_aggregator = JsonDataAggregator(
        max_duration_s=0.5,
        tarfile_aggregator=fake_tarfile_aggregator,
        sensor_name="test_gyroscope",
    )

    sensor = get_gyroscope_sensor(
        json_aggregator=json_aggregator, polling_interval_s=0.1
    )

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
        assert len(sensor_entries) >= 1  # Depends on current user config
        for sensor_entry in sensor_entries:
            assert "rotation_rate_x" in sensor_entry, sensor_entry
            assert "rotation_rate_y" in sensor_entry, sensor_entry
            assert "rotation_rate_z" in sensor_entry, sensor_entry


# TODO complete with microphone and gps sensors!!
