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

    get_conf_value = functools.partial(config.getdefault, "usersettings")

    container_storage = ContainerStorage(encryption_conf=ENCRYTION_CONF,
                                         output_dir=INTERNAL_CONTAINERS_DIR,
                                         max_containers_count=get_conf_value("max_containers_count", 100))

    tarfile_aggregator = TarfileAggregator(
        container_storage=container_storage, max_duration_s=get_conf_value("max_duration_s", 60)
    )

    gyroscope_json_aggregator = JsonAggregator(
        max_duration_s=get_conf_value("max_duration_s", 60),
        tarfile_aggregator=tarfile_aggregator,
        sensor_name="gyroscope")

    gyroscope_sensor = get_periodic_value_provider_gyroscope(json_aggregator=gyroscope_json_aggregator, default_poll_interval_s=0.1)

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

    logger.info("stop_recording_toolchain starts")

    sensors_manager=toolchain["sensors_manager"]
    data_aggregators=toolchain["data_aggregators"]
    tarfile_aggregators=toolchain["tarfile_aggregators"]

    logger.info("Stopping sensors manager")
    sensors_manager.stop()

    logger.info("Joining sensors manager")
    sensors_manager.join()

    logger.info("Flushing data aggregators")
    for data_aggregator in data_aggregators:
        data_aggregator.flush_dataset()

    logger.info("Flushing tarfile aggregators")
    for tarfile_aggregator in tarfile_aggregators:
        tarfile_aggregator.finalize_tarfile()

    logger.info("stop_recording_toolchain exits")

