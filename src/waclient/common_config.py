
from waguilib.importable_settings import *

from wacryptolib.cryptainer import LOCAL_ESCROW_MARKER


# Process parameters #

PACKAGE_NAME = "org.whitemirror.witnessangeldemo"
SERVICE_CLASS = "%s.ServiceRecordingservice" % PACKAGE_NAME

DEFAULT_REQUESTED_PERMISSIONS_MAPPER = {
    # Gyroscope needs no permissions
    # "WRITE_EXTERNAL_STORAGE" => DELAYED PERMISSIONS
    "record_microphone": "RECORD_AUDIO",
    # TODO "CAMERA",
    "record_gps": "ACCESS_FINE_LOCATION"
}


# Source/conf/asset related directories #

WACLIENT_PACKAGE_DIR = Path(__file__).resolve().parent

SRC_ROOT_DIR = WACLIENT_PACKAGE_DIR.parent

DEFAULT_CONFIG_TEMPLATE = WACLIENT_PACKAGE_DIR.joinpath("default_config_template.ini")

DEFAULT_CONFIG_SCHEMA = WACLIENT_PACKAGE_DIR.joinpath("user_settings_schema.json")

APP_CONFIG_FILE = INTERNAL_APP_ROOT / "waclient_config.ini"  # Might no exist yet

_folders_summary = dict(
        WACLIENT_TYPE=WACLIENT_TYPE,
        IS_ANDROID=IS_ANDROID,
        CWD=os.getcwd(),
        SRC_ROOT_DIR=SRC_ROOT_DIR,
        WACLIENT_PACKAGE_DIR=WACLIENT_PACKAGE_DIR,
        INTERNAL_APP_ROOT=INTERNAL_APP_ROOT,
        INTERNAL_CACHE_DIR=INTERNAL_CACHE_DIR,
        INTERNAL_KEYS_DIR=INTERNAL_KEYS_DIR,
        INTERNAL_CRYPTAINER_DIR=INTERNAL_CRYPTAINER_DIR,
        EXTERNAL_DATA_EXPORTS_DIR=EXTERNAL_DATA_EXPORTS_DIR,
)
print(">>>>>>>>>>> SUMMARY OF WAGUILIB FOLDERS CONFIGURATION:", str(_folders_summary))


# Encryption settings #

PREGENERATED_KEY_TYPES = [
    "RSA_OAEP",
    "DSA_DSS",
    "ECC_DSS",
]  # Must be the union of asymmetric encryption/signature keys below

_main_remote_escrow_url = "https://waescrow.prolifik.net/json/"

_PROD_CRYPTOCONF = dict(
    payload_encryption_layers=[
        # First we encrypt with local key and sign via main remote escrow
        dict(
            payload_encryption_algo="AES_EAX",
            key_encryption_layers=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_MARKER
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                )
            ],
        ),
        # Then we encrypt with escrow key and sign via local keys
        dict(
            payload_encryption_algo="AES_CBC",
            key_encryption_layers=[
                dict(
                    key_encryption_algo="RSA_OAEP",
                    key_escrow=dict(escrow_type="jsonrpc", url=_main_remote_escrow_url),
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA256",
                    signature_algo="ECC_DSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                ),
            ],
        )
    ]
)

_TEST_CRYPTOCONF = dict(
    payload_encryption_layers=[
        # We only encrypt/sign with local key, in test environment
        dict(
            payload_encryption_algo="AES_EAX",
            key_encryption_layers=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_MARKER
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="RSA_PSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                )
            ],
        )
    ]
)

def get_cryptoconf(env=""):
    return (
        _TEST_CRYPTOCONF
        if (env and env.upper() == "TEST")
        else _PROD_CRYPTOCONF
    )
