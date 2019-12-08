import os
from pathlib import Path

from kivy import platform
from plyer import storagepath
from typing import List

from wacryptolib.escrow import LOCAL_ESCROW_PLACEHOLDER


ACTIVITY_CLASS = "org.kivy.android.PythonActivity"
SERVICE_CLASS = "org.whitemirror.witnessangeldemo.ServiceRecordingservice"
SERVICE_START_ARGUMENT = ''



print("COMMON CONFIG __file__ >>>>>>", repr(__file__), os.getcwd())

ROOT_DIR = Path(__file__).parents[1]
print("ROOT_DIR >>>>>>", repr(ROOT_DIR))

PACKAGE_DIR = Path(__file__).resolve().parent

DEFAULT_CONFIG_TEMPLATE = Path(__file__).parent.joinpath("default_config_template.ini")
print("DEFAULT_CONFIG_TEMPLATE >>>>>>", repr(DEFAULT_CONFIG_TEMPLATE))



# Internal directories, especially protected on mobile devices

IS_ANDROID = (platform == "android")


if IS_ANDROID:
    from jnius import autoclass
    from android import mActivity
    #print("mActivity.getFilesDir()", (mActivity.getFilesDir().toString()) if mActivity else None)
    if mActivity:
        INTERNAL_APP_ROOT = Path(mActivity.getFilesDir().toString())
    else:
        # WE ARE IN SERVICE!!!
        service = autoclass('org.kivy.android.PythonService').mService
        #service_class = autoclass(SERVICE_CLASS)
        #service = service_class.mService
        #print(">>>>>>>>>>>>>>>>>>>service", service)
        #print("service.getFilesDir()", service.getFilesDir().toString())
        INTERNAL_APP_ROOT = Path(service.getFilesDir().toString())
    Context = autoclass('android.content.Context')
    _EXTERNAL_APP_ROOT = Path(Context.getExternalFilesDirs().toString()) / "WitnessAngel"
    """
    Environment = autoclass('android.os.Environment')
    print("Environment.getExternalStorageDirectory()", Environment.getExternalStorageDirectory().toString())
    
    #print("Context.getExternalFilesDirs()", Context.getExternalFilesDirs(XXXXX))
    """
else:
    INTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelInternal"
    _EXTERNAL_APP_ROOT = Path(storagepath.get_home_dir()) / "WitnessAngelExternal"
INTERNAL_APP_ROOT.mkdir(exist_ok=True)

APP_CONFIG_FILE = INTERNAL_APP_ROOT / "app_config.ini"  # Might no exist yet

print ("LOCAL PATH FOUND:", INTERNAL_APP_ROOT, _EXTERNAL_APP_ROOT)

'''
INTERNAL_APP_ROOT = Path("/data/data/org.whitemirror.witnessangeldemo")  #Path(storagepath.get_application_dir())
print("TRYING APP FOLDER1", INTERNAL_APP_ROOT)
if not os.path.exists(INTERNAL_APP_ROOT):

    print("TRYING APP FOLDER2", INTERNAL_APP_ROOT)
    INTERNAL_APP_ROOT.mkdir(exist_ok=True)
'''

INTERNAL_KEYS_DIR = INTERNAL_APP_ROOT / "KeyStorage"
#print("TRYING INTERNAL_KEYS_DIR", INTERNAL_KEYS_DIR)
INTERNAL_KEYS_DIR.mkdir(exist_ok=True)

INTERNAL_CONTAINERS_DIR = INTERNAL_APP_ROOT / "Containers"
INTERNAL_CONTAINERS_DIR.mkdir(exist_ok=True)


EXTERNAL_DATA_EXPORTS_DIR = _EXTERNAL_APP_ROOT / "DataExports"  # Might no exist yet

'''
# External directories, shared by applications
try:
    #storagepath.get_sdcard_dir()
    _EXTERNAL_APP_ROOT = Path("/storage/emulated/0/WitnessAngel")
    if not os.path.exists(_EXTERNAL_APP_ROOT):
        raise NotImplementedError
except NotImplementedError:
'''




def request_multiple_permissions(permissions: List[str]) -> List[bool]:
    """Returns nothing."""
    if IS_ANDROID:
        from android.permissions import request_permissions, Permission
        permission_objs = [getattr(Permission, permission) for permission in permissions]
        request_permissions(permission_objs)  # Might freeze app while showing user a popup


def request_single_permission(permission: str) -> bool:
    """Returns True iff permission was immediately granted."""
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





FREE_KEY_TYPES = ["RSA", "DSA"]  # Must be the union of asymmetric encryption/signature keys below

_main_remote_escrow_url = "http://127.0.0.1:8000/json/"

_PROD_ENCRYPTION_CONF = dict(
    data_encryption_strata=[
        # First we encrypt with local key and sign via main remote escrow
        dict(
            data_encryption_algo="AES_EAX",
            key_encryption_strata=[
                dict(
                    escrow_key_type="RSA",
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
            data_signatures=[
                dict(
                    signature_key_type="RSA",
                    message_prehash_algo="SHA512",
                    signature_algo="PSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        ),
])
"""
        # Then we encrypt with escrow key and sign via local keys
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(
                    escrow_key_type="RSA",
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=dict(url=_main_remote_escrow_url),
                )
            ],
            data_signatures=[
                dict(
                    signature_key_type="DSA",
                    message_prehash_algo="SHA256",
                    signature_algo="DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                ),
            ],
        )
    ]
)"""

_TEST_ENCRYPTION_CONF = dict(
    data_encryption_strata=[
        # We only encrypt/sign with local key, in test environment
        dict(
            data_encryption_algo="AES_EAX",
            key_encryption_strata=[
                dict(
                    escrow_key_type="RSA",
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
            data_signatures=[
                dict(
                    signature_key_type="RSA",
                    message_prehash_algo="SHA512",
                    signature_algo="PSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        )
    ]
)


def get_encryption_conf(env=""):
    return _TEST_ENCRYPTION_CONF if (env and env.upper() == "TEST") else _PROD_ENCRYPTION_CONF
