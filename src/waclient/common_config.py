import os
from pathlib import Path

from plyer import storagepath

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

INTERNAL_CONTAINERS_DIR = APP_DIR / ".containers"
INTERNAL_CONTAINERS_DIR.mkdir(exist_ok=True)
