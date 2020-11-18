import os
import time

from kivy.config import ConfigParser

from _waclient_test_utilities import purge_test_containers
from waclient.common_config import (
    INTERNAL_CONTAINERS_DIR,
    INTERNAL_KEYS_DIR,
    get_encryption_conf,
)
from waclient.recording_toolchain import (
    build_recording_toolchain,
    start_recording_toolchain,
    stop_recording_toolchain,
)
from wacryptolib.key_storage import FilesystemKeyStorage, FilesystemKeyStoragePool
from wacryptolib.sensor import TarfileRecordsAggregator
from wacryptolib.utilities import load_from_json_bytes


def test_nominal_recording_toolchain_case():

    config = ConfigParser()  # Empty but OK
    config.setdefaults("usersettings",
                       {"record_gyroscope": 1,
                        "record_gps": 1,
                        "record_microphone": 1})

    key_storage_pool = FilesystemKeyStoragePool(INTERNAL_KEYS_DIR)
    encryption_conf = get_encryption_conf("test")
    toolchain = build_recording_toolchain(
        config, key_storage_pool=key_storage_pool, encryption_conf=encryption_conf
    )
    sensors_manager = toolchain["sensors_manager"]
    data_aggregators = toolchain["data_aggregators"]
    tarfile_aggregators = toolchain["tarfile_aggregators"]
    container_storage = toolchain["container_storage"]

    purge_test_containers()

    # TODO - make this a PURGE() methods of storage!!!
    # CLEANUP of already existing containers
    # for container_name in container_storage.list_container_names(sorted=True):
    #    container_storage._delete_container(container_name)
    # assert not len(container_storage)

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
    (container_name,) = container_storage.list_container_names(as_sorted=True)

    tarfile_bytestring = container_storage.decrypt_container_from_storage(
        container_name
    )

    tar_file = TarfileRecordsAggregator.read_tarfile_from_bytestring(tarfile_bytestring)
    tarfile_members = tar_file.getnames()
    assert len(tarfile_members) == 3

    # Gyroscope data

    gyroscope_filenames = [m for m in tarfile_members if "gyroscope" in m]
    assert len(gyroscope_filenames) == 1
    assert gyroscope_filenames[0].endswith(".json")

    json_bytestring = tar_file.extractfile(gyroscope_filenames[0]).read()
    gyroscope_data = load_from_json_bytes(json_bytestring)
    assert isinstance(gyroscope_data, list)
    assert len(gyroscope_data) >= 4
    assert gyroscope_data[0] == {
        "rotation_rate_x": None,
        "rotation_rate_y": None,
        "rotation_rate_z": None,
    }

    # GPS data

    microphone_filenames = [m for m in tarfile_members if "gps" in m]
    assert len(microphone_filenames) == 1
    assert microphone_filenames[0].endswith(".json")

    json_bytestring = tar_file.extractfile(microphone_filenames[0]).read()
    gyroscope_data = load_from_json_bytes(json_bytestring)
    # Fake data pushed by sensor
    assert gyroscope_data == [{'altitude': 2.2}, {'message_type': 'some_message_type', 'status': 'some_status_value'}]

    # Microphone data

    microphone_filenames = [m for m in tarfile_members if "microphone" in m]
    assert len(microphone_filenames) == 1
    assert microphone_filenames[0].endswith(".mp4")

    mp4_bytestring = tar_file.extractfile(microphone_filenames[0]).read()
    assert mp4_bytestring == b"fake_microphone_recording_data"
