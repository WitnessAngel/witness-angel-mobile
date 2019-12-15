import os

from waclient.common_config import INTERNAL_CONTAINERS_DIR


def list_test_containers():
    return [
        os.path.join(INTERNAL_CONTAINERS_DIR, filename)
        for filename in os.listdir(INTERNAL_CONTAINERS_DIR)
    ]


def purge_test_containers():
    for filepath in list_test_containers():
        os.remove(filepath)
