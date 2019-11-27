import time

from kivy.config import ConfigParser

from waclient.recording_toolchain import build_recording_toolchain, start_recording_toolchain, stop_recording_toolchain
from wacryptolib.sensor import TarfileAggregator
from wacryptolib.utilities import load_from_json_bytes


def test_nominal_recording_case():

    config = ConfigParser()  # Empty but OK

    toolchain = build_recording_toolchain(config)
    sensors_manager=toolchain["sensors_manager"]
    data_aggregators=toolchain["data_aggregators"]
    tarfile_aggregators=toolchain["tarfile_aggregators"]
    container_storage = toolchain["container_storage"]

    # TODO - make this a PURGE() methods of storage!!!
    # CLEANUP of already existing containers
    for container_name in container_storage.list_container_names(as_sorted_relative_paths=True):
        container_storage._delete_container(container_name)
    assert not len(container_storage)

    start_recording_toolchain(toolchain)
    time.sleep(2)
    stop_recording_toolchain(toolchain)

    for i in range(2):
        assert not sensors_manager.is_running
        for data_aggregator in data_aggregators:
            assert len(data_aggregator) == 0
        for tarfile_aggregator in tarfile_aggregators:
            assert len(tarfile_aggregator) == 0
        time.sleep(1)

    assert len(container_storage) == 1  # Too quick recording to have container rotation
    (container_name,) = container_storage.list_container_names(as_sorted_relative_paths=True)

    tarfile_bytestring = container_storage.decrypt_container_from_storage(container_name)

    tar_file = TarfileAggregator.read_tarfile_from_bytestring(tarfile_bytestring)
    tarfile_members = tar_file.getnames()
    assert len(tarfile_members) == 1

    json_filename = tarfile_members[0]
    assert json_filename.endswith(".json")
    assert "gyroscope" in json_filename

    json_bytestring = tar_file.extractfile(json_filename).read()
    gyroscope_data = load_from_json_bytes(json_bytestring)

    assert isinstance(gyroscope_data, list)
    assert len(gyroscope_data) > 15
    assert gyroscope_data[0] == {'rotation_x': None, 'rotation_y': None, 'rotation_z': None}
