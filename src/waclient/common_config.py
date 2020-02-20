import os
from pathlib import Path
from typing import List

from kivy import platform
from plyer import storagepath

from wacryptolib.escrow import LOCAL_ESCROW_PLACEHOLDER


PACKAGE_NAME = "org.whitemirror.witnessangeldemo"

ACTIVITY_CLASS = "org.kivy.android.PythonActivity"
SERVICE_CLASS = "%s.ServiceRecordingservice" % PACKAGE_NAME
SERVICE_START_ARGUMENT = ""
REQUESTED_PERMISSIONS = [
    "WRITE_EXTERNAL_STORAGE",
    "RECORD_AUDIO",
    "CAMERA",
    "ACCESS_FINE_LOCATION"
]
IS_ANDROID = (platform == "android")

WACLIENT_TYPE = os.environ.get("WACLIENT_TYPE", "<UNKNOWN>")


# Source/conf/asset related directories

WACLIENT_PACKAGE_DIR = Path(__file__).resolve().parent

SRC_ROOT_DIR = WACLIENT_PACKAGE_DIR.parent

DEFAULT_CONFIG_TEMPLATE = WACLIENT_PACKAGE_DIR.joinpath("default_config_template.ini")

DEFAULT_CONFIG_SCHEMA = WACLIENT_PACKAGE_DIR.joinpath("user_settings_schema.json")


# Internal directories, specifically protected on mobile devices


if IS_ANDROID:
    from jnius import autoclass
    from android import mActivity

    if mActivity:
        # WE ARE IN MAIN APP (safer than WACLIENT_TYPE)
        INTERNAL_APP_ROOT = Path(mActivity.getFilesDir().toString())
        INTERNAL_CACHE_DIR = Path(mActivity.getCacheDir().toString())
    else:
        # WE ARE IN SERVICE!!!
        service = autoclass("org.kivy.android.PythonService").mService
        INTERNAL_APP_ROOT = Path(service.getFilesDir().toString())
        INTERNAL_CACHE_DIR = Path(service.getCacheDir().toString())
    Environment = autoclass("android.os.Environment")
    _EXTERNAL_APP_ROOT = (
        Path(Environment.getExternalStorageDirectory().toString()) / "WitnessAngel"
    )
else:
    INTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelInternal"
    _EXTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelExternal"
    INTERNAL_CACHE_DIR = Path(storagepath.get_home_dir()) / "WitnessAngelCache"
INTERNAL_APP_ROOT.mkdir(exist_ok=True)
INTERNAL_CACHE_DIR.mkdir(exist_ok=True)

APP_CONFIG_FILE = INTERNAL_APP_ROOT / "app_config.ini"  # Might no exist yet

# Created/deleted by app, looked up by daemon service on boot/restart
WIP_RECORDING_MARKER = INTERNAL_APP_ROOT / "recording_in_progress"  

INTERNAL_KEYS_DIR = INTERNAL_APP_ROOT / "KeyStorage"
INTERNAL_KEYS_DIR.mkdir(exist_ok=True)

INTERNAL_CONTAINERS_DIR = INTERNAL_APP_ROOT / "Containers"
INTERNAL_CONTAINERS_DIR.mkdir(exist_ok=True)

EXTERNAL_DATA_EXPORTS_DIR = _EXTERNAL_APP_ROOT / "DataExports"  # Might no exist yet (and require permissions!)


_folders_summary = dict(
        WACLIENT_TYPE=WACLIENT_TYPE,
        IS_ANDROID=IS_ANDROID,
        CWD=os.getcwd(),
        SRC_ROOT_DIR=SRC_ROOT_DIR,
        WACLIENT_PACKAGE_DIR=WACLIENT_PACKAGE_DIR,
        INTERNAL_APP_ROOT=INTERNAL_APP_ROOT,
        INTERNAL_CACHE_DIR=INTERNAL_CACHE_DIR,
        INTERNAL_KEYS_DIR=INTERNAL_KEYS_DIR,
        INTERNAL_CONTAINERS_DIR=INTERNAL_CONTAINERS_DIR,
        EXTERNAL_DATA_EXPORTS_DIR=EXTERNAL_DATA_EXPORTS_DIR,
)
print(">>>>>>>>>>> SUMMARY OF WACLIENT COMMON CONFIGURATION:", str(_folders_summary))


def request_multiple_permissions(permissions: List[str]) -> List[bool]:
    """Returns nothing."""
    if IS_ANDROID:
        from android.permissions import request_permissions, Permission

        permission_objs = [
            getattr(Permission, permission) for permission in permissions
        ]
        request_permissions(
            permission_objs
        )  # Might freeze app while showing user a popup


def request_single_permission(permission: str) -> bool:
    """Returns True iff permission was immediately granted."""
    assert permission in REQUESTED_PERMISSIONS, permission
    if IS_ANDROID:
        from android.permissions import check_permission, Permission

        request_multiple_permissions([permission])
        return check_permission(getattr(Permission, permission))
    return True  # For desktop OS


def request_external_storage_dirs_access():
    """Ask for write permission and create missing directories."""
    res = request_single_permission("WRITE_EXTERNAL_STORAGE")
    if res:
        EXTERNAL_DATA_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    return res


PREGENERATED_KEY_TYPES = [
    "RSA_OAEP",
    "DSA_DSS",
    "ECC_DSS",
]  # Must be the union of asymmetric encryption/signature keys below

_main_remote_escrow_url = "https://waescrow.prolifik.net/json/"

_PROD_ENCRYPTION_CONF = dict(
    data_encryption_strata=[
        # First we encrypt with local key and sign via main remote escrow
        dict(
            data_encryption_algo="AES_EAX",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_PLACEHOLDER
                )
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        ),
        # Then we encrypt with escrow key and sign via local keys
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=dict(url=_main_remote_escrow_url),
                )
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA256",
                    signature_algo="ECC_DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                ),
            ],
        )
    ]
)

_TEST_ENCRYPTION_CONF = dict(
    data_encryption_strata=[
        # We only encrypt/sign with local key, in test environment
        dict(
            data_encryption_algo="AES_EAX",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_PLACEHOLDER
                )
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="RSA_PSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        )
    ]
)


def get_encryption_conf(env=""):
    return (
        _TEST_ENCRYPTION_CONF
        if (env and env.upper() == "TEST")
        else _PROD_ENCRYPTION_CONF
    )
