import os
from pathlib import Path

from plyer import storagepath

from wacryptolib.escrow import LOCAL_ESCROW_PLACEHOLDER

ROOT_DIR = Path(__file__).parents[1]
print("ROOT_DIR", repr(ROOT_DIR))

PACKAGE_DIR = Path(__file__).parent

CONFIG_FILE = PACKAGE_DIR / "witnessangelclient.ini"
assert CONFIG_FILE.exists(), CONFIG_FILE

APP_DIR = storagepath.get_application_dir()
if not os.path.exists(APP_DIR):
    APP_DIR = storagepath.get_home_dir()
APP_DIR = Path(APP_DIR)
print("APP_DIR", repr(APP_DIR))

INTERNAL_CONTAINERS_DIR = APP_DIR / ".wacontainers"
INTERNAL_CONTAINERS_DIR.mkdir(exist_ok=True)

ENCRYTION_CONF = dict(
    data_encryption_strata=[
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(
                    escrow_key_type="RSA",
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
            data_signatures=[
                dict(
                    signature_key_type="DSA",
                    signature_algo="DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        )
    ]
)
