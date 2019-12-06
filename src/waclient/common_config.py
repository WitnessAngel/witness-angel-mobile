import os
from pathlib import Path

from plyer import storagepath

from wacryptolib.escrow import LOCAL_ESCROW_PLACEHOLDER

ROOT_DIR = Path(__file__).parents[1]
print("ROOT_DIR", repr(ROOT_DIR))

PACKAGE_DIR = Path(__file__).parent

CONFIG_FILE = PACKAGE_DIR / "witnessangelclient.ini"
assert CONFIG_FILE.exists(), CONFIG_FILE

# Internal directories, especially protected on mobile devices

INTERNAL_APP_ROOT = Path(storagepath.get_application_dir())
if not os.path.exists(INTERNAL_APP_ROOT):
    INTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelInternal"
    INTERNAL_APP_ROOT.mkdir(exist_ok=True)

INTERNAL_KEYS_DIR = INTERNAL_APP_ROOT / "KeyStorage"
INTERNAL_KEYS_DIR.mkdir(exist_ok=True)

INTERNAL_CONTAINERS_DIR = INTERNAL_APP_ROOT / "Containers"
INTERNAL_CONTAINERS_DIR.mkdir(exist_ok=True)

# External directories, shared by applications
try:
    EXTERNAL_APP_ROOT = Path(storagepath.get_sdcard_dir()) / "WitnessAngel"
except NotImplementedError:
    EXTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelExternal"
    EXTERNAL_APP_ROOT.mkdir(exist_ok=True)

EXTERNAL_DATA_EXPORTS_DIR = EXTERNAL_APP_ROOT / "DataExports"
EXTERNAL_DATA_EXPORTS_DIR.mkdir(exist_ok=True)

FREE_KEY_TYPES = ["RSA", "DSA"]  # Must be the union of asymmetric encryption/signature keys below
ENCRYPTION_CONF = dict(
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
                    message_prehash_algo="SHA256",
                    signature_algo="DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                ),
                dict(
                    signature_key_type="RSA",
                    message_prehash_algo="SHA512",
                    signature_algo="PSS",
                    signature_escrow=dict(url="http://127.0.0.1:8000/json/"),
                )
            ],
        )
    ]
)
