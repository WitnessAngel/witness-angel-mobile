import time

from wacryptolib.container import TarfileAggregator
from wacryptolib.utilities import load_from_json_bytes


class FakeTarfileAggregator(TarfileAggregator):

    def __init__(self):
        self._test_records = []

    def add_record(self, **kwargs):
        print("AAAD")
        self._test_records.append(kwargs)

    def finalize_tarfile(self):
        print("FINALIZZE")
        self._test_records = []


def test_gyroscope():

    from waclient.sensors.gyroscope import get_periodic_value_provider

    fake_tarfile_aggregator = FakeTarfileAggregator()

    sensor = get_periodic_value_provider(tarfile_aggregator=fake_tarfile_aggregator, default_chunk_duration_s=0.5, default_poll_interval_s=0.1)

    sensor.start()

    time.sleep(0.9)

    sensor.stop()
    sensor.join()

    sensor._json_aggregator.flush_dataset()

    assert not sensor._json_aggregator._current_dataset

    #assert len(fake_tarfile_aggregator._test_records) == 2

    print(fake_tarfile_aggregator._test_records)

    for record in fake_tarfile_aggregator._test_records:
        sensor_entries = load_from_json_bytes(record["data"])
        assert len(sensor_entries) >= 3
        for sensor_entry in sensor_entries:
            assert "rotation_x" in sensor_entry, sensor_entry
            assert "rotation_y" in sensor_entry, sensor_entry
            assert "rotation_z" in sensor_entry, sensor_entry

