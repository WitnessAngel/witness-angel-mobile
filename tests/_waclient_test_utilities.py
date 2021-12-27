import os

from waclient.common_config import INTERNAL_CRYPTAINER_DIR


def list_test_cryptainers():
    return [
        os.path.join(INTERNAL_CRYPTAINER_DIR, filename)
        for filename in os.listdir(INTERNAL_CRYPTAINER_DIR)
        if filename.endswith(".crypt")  # Ignore offloaded data files
    ]


def purge_test_cryptainers():
    for filepath in list_test_cryptainers():
        os.remove(filepath)
