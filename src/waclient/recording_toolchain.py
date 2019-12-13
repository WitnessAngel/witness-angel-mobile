import functools

from oscpy.server import OSCThreadServer

from waclient.common_config import INTERNAL_CONTAINERS_DIR, INTERNAL_KEYS_DIR, FREE_KEY_TYPES, IS_ANDROID
from waclient.sensors.gps import get_gps_sensor
from waclient.sensors.gyroscope import get_gyroscope_sensor
from waclient.sensors.microphone import get_microphone_sensor
from wacryptolib.container import ContainerStorage
from wacryptolib.escrow import get_free_keys_generator_worker
from wacryptolib.key_storage import FilesystemKeyStorage
from wacryptolib.sensor import TarfileRecordsAggregator, JsonDataAggregator, SensorsManager

from kivy.logger import Logger as logger


osc = OSCThreadServer(encoding="utf8")


if IS_ANDROID:
    # Due to bug in JNI, we must ensure some classes are found first from MAIN process thread!
    from jnius import autoclass
    autoclass('org.jnius.NativeInvocationHandler')


def build_recording_toolchain(config, local_key_storage, encryption_conf):
    """Instantiate the whole toolchain of sensors and aggregators, depending on the config."""

    # TODO make this part more resilient against exceptions

    def get_conf_value(*args, converter=None, **kwargs):
        value = config.getdefault("usersettings", *args, **kwargs)
        if converter:
            value = converter(value)
        return value

    max_containers_count=get_conf_value("max_containers_count", 100, converter=int)
    container_recording_duration_s=get_conf_value("container_recording_duration_s", 60, converter=float)
    container_member_duration_s=get_conf_value("container_member_duration_s", 60, converter=float)
    polling_interval_s=get_conf_value("polling_interval_s", 0.5, converter=float)
    max_free_keys_per_type=get_conf_value("max_free_keys_per_type", 5, converter=int)

    logger.info("Toolchain configuration is %s",
                str(dict(max_containers_count=max_containers_count,
                         container_recording_duration_s=container_recording_duration_s,
                         container_member_duration_s=container_member_duration_s,
                         polling_interval_s=polling_interval_s)))

    container_storage = ContainerStorage(encryption_conf=encryption_conf,
                                         containers_dir=INTERNAL_CONTAINERS_DIR,
                                         max_containers_count=max_containers_count,
                                         local_key_storage=local_key_storage)

    # Tarfile builder level

    tarfile_aggregator = TarfileRecordsAggregator(
        container_storage=container_storage, max_duration_s=container_recording_duration_s)

    # Data aggregation level

    gyroscope_json_aggregator = JsonDataAggregator(
        max_duration_s=container_member_duration_s,
        tarfile_aggregator=tarfile_aggregator,
        sensor_name="gyroscope")

    gps_json_aggregator = JsonDataAggregator(
        max_duration_s=container_member_duration_s,
        tarfile_aggregator=tarfile_aggregator,
        sensor_name="gps")

    # Sensors level

    gyroscope_sensor = get_gyroscope_sensor(json_aggregator=gyroscope_json_aggregator, polling_interval_s=polling_interval_s)

    gps_sensor = get_gps_sensor(polling_interval_s=polling_interval_s, json_aggregator=gps_json_aggregator)

    microphone_sensor = get_microphone_sensor(interval_s=container_member_duration_s,
                                              tarfile_aggregator=tarfile_aggregator)

    sensors = [gyroscope_sensor, gps_sensor, microphone_sensor]
    sensors_manager = SensorsManager(sensors=sensors)

    # Off-band workers

    free_keys_generator_worker = get_free_keys_generator_worker(
                                        key_storage=local_key_storage,
                                        max_free_keys_per_type=max_free_keys_per_type,
                                        sleep_on_overflow_s=0.5 * max_free_keys_per_type * container_member_duration_s, #TODO make it configurable?
                                        key_types=FREE_KEY_TYPES
    )

    toolchain = dict(sensors_manager=sensors_manager,
                     data_aggregators=[gyroscope_json_aggregator, gps_json_aggregator],
                     tarfile_aggregators=[tarfile_aggregator],
                     container_storage=container_storage,
                     free_keys_generator_worker=free_keys_generator_worker,
                     local_key_storage=local_key_storage)
    return toolchain


def start_recording_toolchain(toolchain):
    """
    Start all the sensors, thus ensuring that the toolchain begins to record end-to-end.
    """

    logger.info("Starting the generator of free keys")
    free_keys_generator_worker = toolchain["free_keys_generator_worker"]
    free_keys_generator_worker.start()

    sensors_manager=toolchain["sensors_manager"]
    sensors_manager.start()


def stop_recording_toolchain(toolchain):
    """
    Perform an ordered stop+flush of sensors and miscellaneous layers of aggregator.

    All objets remain in a usable state
    """

    # TODO push all this to sensor manager!!

    #logger.info("stop_recording_toolchain starts")

    sensors_manager=toolchain["sensors_manager"]
    data_aggregators=toolchain["data_aggregators"]
    tarfile_aggregators=toolchain["tarfile_aggregators"]
    container_storage=toolchain["container_storage"]
    free_keys_generator_worker = toolchain["free_keys_generator_worker"]

    logger.info("Stopping the generator of free keys")
    free_keys_generator_worker.stop()

    #logger.info("Stopping sensors manager")
    sensors_manager.stop()

    #logger.info("Joining sensors manager")
    sensors_manager.join()

    for idx, data_aggregator in enumerate(data_aggregators, start=1):
        logger.info("Flushing '%s' data aggregator" % data_aggregator.sensor_name)
        data_aggregator.flush_dataset()

    for idx, tarfile_aggregator in enumerate(tarfile_aggregators, start=1):
        logger.info("Flushing tarfile builder" + (" #%d" % idx if (len(tarfile_aggregators) > 1) else ""))
        tarfile_aggregator.finalize_tarfile()

    container_storage.wait_for_idle_state()  # Encryption workers must finish their job

    #logger.info("stop_recording_toolchain exits")

