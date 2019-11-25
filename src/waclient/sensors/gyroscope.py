

from plyer import gyroscope
from wacryptolib.container import JsonAggregator, PeriodicValuePoller


def get_periodic_value_provider(tarfile_aggregator, default_chunk_duration_s, default_poll_interval_s):

    json_aggregator = JsonAggregator(
        max_duration_s=default_chunk_duration_s,
        tarfile_aggregator=tarfile_aggregator,
        sensor_name="gyroscope",
    )

    def get_gyroscope_rotation():
        try:
            rotation = gyroscope.rotation
        except NotImplementedError:
            # TODO logging or warnings here?
            rotation = (None, None, None)
        rotation_dict = {"rotation_x": rotation[0],
                         "rotation_y": rotation[1],
                         "rotation_z": rotation[2]}
        print("Returning rotation", rotation_dict)
        return rotation_dict

    poller = PeriodicValuePoller(
        interval_s=default_poll_interval_s, task_func=get_gyroscope_rotation, json_aggregator=json_aggregator)

    return poller
