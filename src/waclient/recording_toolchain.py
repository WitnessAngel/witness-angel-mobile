import functools

from oscpy.server import OSCThreadServer

from waclient.common_config import INTERNAL_CONTAINERS_DIR, ENCRYTION_CONF
from waclient.sensors.gyroscope import get_periodic_value_provider as get_periodic_value_provider_gyroscope
from wacryptolib.container import ContainerStorage
from wacryptolib.sensor import TarfileAggregator, JsonAggregator, SensorManager

from kivy.logger import Logger as logger


osc = OSCThreadServer(encoding="utf8")




def build_recording_toolchain(config):
    """Instantiate the whole toolchain of sensors and aggregators, depending on the config."""

    def get_conf_value(*args, converter=None, **kwargs):
        value = config.getdefault("usersettings", *args, **kwargs)
        if converter:
            value = converter(value)
        return value

    max_containers_count=get_conf_value("max_containers_count", 100, converter=int)
    container_recording_duration_s=get_conf_value("container_recording_duration_s", 60, converter=float)
    container_member_duration_s=get_conf_value("container_member_duration_s", 60, converter=float)
    polling_interval_s=get_conf_value("polling_interval_s", 1.0, converter=float)

    logger.info("Toolchain configuration is %s",
                str(dict(max_containers_count=max_containers_count,
                         container_recording_duration_s=container_recording_duration_s,
                         container_member_duration_s=container_member_duration_s,
                         polling_interval_s=polling_interval_s)))

    container_storage = ContainerStorage(encryption_conf=ENCRYTION_CONF,
                                         output_dir=INTERNAL_CONTAINERS_DIR,
                                         max_containers_count=max_containers_count)

    tarfile_aggregator = TarfileAggregator(
        container_storage=container_storage, max_duration_s=container_recording_duration_s)

    gyroscope_json_aggregator = JsonAggregator(
        max_duration_s=container_member_duration_s,
        tarfile_aggregator=tarfile_aggregator,
        sensor_name="gyroscope")

    gyroscope_sensor = get_periodic_value_provider_gyroscope(json_aggregator=gyroscope_json_aggregator, polling_interval_s=polling_interval_s)

    sensors = [gyroscope_sensor]
    sensors_manager = SensorManager(sensors=sensors)

    toolchain = dict(sensors_manager=sensors_manager,
                    data_aggregators=[gyroscope_json_aggregator],
                    tarfile_aggregators=[tarfile_aggregator],
                    container_storage=container_storage)
    return toolchain


def start_recording_toolchain(toolchain):
    """
    Start all the sensors, thus ensuring that the toolchain begins to record end-to-end.
    """
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

    logger.info("Stopping sensors manager")
    sensors_manager.stop()

    logger.info("Joining sensors manager")
    sensors_manager.join()

    for idx, data_aggregator in enumerate(data_aggregators, start=1):
        logger.info("Flushing data aggregator #%d", idx)
        data_aggregator.flush_dataset()

    for idx, tarfile_aggregator in enumerate(tarfile_aggregators, start=1):
        logger.info("Flushing tarfile aggregator #%d", idx)
        tarfile_aggregator.finalize_tarfile()

    #logger.info("stop_recording_toolchain exits")

