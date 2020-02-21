import os
from pathlib import Path
import time
from typing import List

from kivy import platform

from plyer import storagepath

from wacryptolib.escrow import LOCAL_ESCROW_PLACEHOLDER


PACKAGE_NAME = "org.whitemirror.witnessangeldemo"

ACTIVITY_CLASS = "org.kivy.android.PythonActivity"
SERVICE_CLASS = "%s.ServiceRecordingservice" % PACKAGE_NAME
SERVICE_START_ARGUMENT = ""
DEFAULT_REQUESTED_PERMISSIONS_MAPPER = {
    # Gyroscope needs no permissions
    # "WRITE_EXTERNAL_STORAGE" => DELAYED PERMISSIONS
    "record_microphone": "RECORD_AUDIO",
    # TODO "CAMERA",
    "record_gps": "ACCESS_FINE_LOCATION"
}
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
        CONTEXT = mActivity
    else:
        # WE ARE IN SERVICE!!!
        CONTEXT = autoclass("org.kivy.android.PythonService").mService

    INTERNAL_APP_ROOT = Path(CONTEXT.getFilesDir().toString())
    INTERNAL_CACHE_DIR = Path(CONTEXT.getCacheDir().toString())
    Environment = autoclass("android.os.Environment")
    _EXTERNAL_APP_ROOT = (
        Path(Environment.getExternalStorageDirectory().toString()) / "WitnessAngel"
    )

    PackageManager = autoclass('android.content.pm.PackageManager')  # Precached for permission checking


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
        permissions_qualified_names = [
            getattr(Permission, permission) for permission in permissions
        ]
        request_permissions(
                permissions_qualified_names
        )  # Might freeze app while showing user a popup


def request_single_permission(permission: str) -> bool:
    """Returns nothing."""
    request_multiple_permissions([permission])


def has_single_permission(permission: str) -> bool:
    """Returns True iff permission was granted."""
    from kivy.logger import Logger as logger  # Delayed import
    if IS_ANDROID:
        # THIS ONLY WORKS FOR ACTIVITIES: "from android.permissions import check_permission, Permission"
        from jnius import autoclass
        from android.permissions import Permission
        permission_qualified_name = getattr(Permission, permission)  # e.g. android.permission.ACCESS_FINE_LOCATION
        res = CONTEXT.checkSelfPermission(permission_qualified_name)
        #logger.info("checkSelfPermission returned %r (vs %s) for %s" % (res, PackageManager.PERMISSION_GRANTED, permission))
        return (res == PackageManager.PERMISSION_GRANTED)
    return True  # For desktop OS


def warn_if_permission_missing(permission: str) -> bool:
    """Returns True iff a warning was emitted and permission is missing."""
    from kivy.logger import Logger as logger  # Delayed import
    if IS_ANDROID:
        if not has_single_permission(permission=permission):
            logger.warning("Missing permission %s, cancelling use of corresponding sensor" % permission)
            return True
    return False


def request_external_storage_dirs_access():
    """Ask for write permission and create missing directories."""
    from kivy.logger import Logger as logger  # Delayed import
    permission = "WRITE_EXTERNAL_STORAGE"
    request_single_permission(permission)
    # FIXME remove this ugly sleep() hack and move this to Service
    time.sleep(3)  # Let the callback permission request be processed
    res = has_single_permission(permission)
    #logger.info("Has single permission %r is %s" % (permission, res))
    if res:
        EXTERNAL_DATA_EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
        return True
    return False


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
