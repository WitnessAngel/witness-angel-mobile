
from wacomponents.default_settings import *

from wacryptolib.cryptainer import LOCAL_KEYFACTORY_TRUSTEE_MARKER


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
        INTERNAL_KEYSTORE_POOL_DIR=INTERNAL_KEYSTORE_POOL_DIR,
        INTERNAL_CRYPTAINER_DIR=INTERNAL_CRYPTAINER_DIR,
        EXTERNAL_EXPORTS_DIR=EXTERNAL_EXPORTS_DIR,
)
print(">>>>>>>>>>> SUMMARY OF WACOMPONENTS FOLDERS CONFIGURATION:", str(_folders_summary))


# Encryption settings #

PREGENERATED_KEY_TYPES = [
    "RSA_OAEP",
    "DSA_DSS",
    "ECC_DSS",
]  # Must be the union of asymmetric encryption/signature keys below

_main_remote_trustee_url = "https://watrustee.prolifik.net/json/"

_PROD_CRYPTOCONF = dict(
    payload_cipher_layers=[
        # First we encrypt with local key and sign via main remote trustee
        dict(
            payload_cipher_algo="AES_EAX",
            key_cipher_layers=[
                dict(
                    key_cipher_algo="RSA_OAEP", key_cipher_trustee=LOCAL_KEYFACTORY_TRUSTEE_MARKER
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    payload_signature_algo="DSA_DSS",
                    payload_signature_trustee=LOCAL_KEYFACTORY_TRUSTEE_MARKER,
                )
            ],
        ),
        # Then we encrypt with trustee key and sign via local keys
        dict(
            payload_cipher_algo="AES_CBC",
            key_cipher_layers=[
                dict(
                    key_cipher_algo="RSA_OAEP",
                    key_cipher_trustee=dict(trustee_type="jsonrpc", url=_main_remote_trustee_url),
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA256",
                    payload_signature_algo="ECC_DSS",
                    payload_signature_trustee=LOCAL_KEYFACTORY_TRUSTEE_MARKER,
                ),
            ],
        )
    ]
)

_TEST_CRYPTOCONF = dict(
    payload_cipher_layers=[
        # We only encrypt/sign with local key, in test environment
        dict(
            payload_cipher_algo="AES_EAX",
            key_cipher_layers=[
                dict(
                    key_cipher_algo="RSA_OAEP", key_cipher_trustee=LOCAL_KEYFACTORY_TRUSTEE_MARKER
                )
            ],
            payload_signatures=[
                dict(
                    message_prehash_algo="SHA512",
                    payload_signature_algo="RSA_PSS",
                    payload_signature_trustee=LOCAL_KEYFACTORY_TRUSTEE_MARKER,
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
