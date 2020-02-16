import sys, os
from configparser import ConfigParser
from pathlib import Path
import logging

logger = logging.getLogger('p4a')

THIS_DIR = Path(__file__).absolute()
BUILDOZER_SPEC_PATH = THIS_DIR.parents[1].joinpath("buildozer.spec")
assert BUILDOZER_SPEC_PATH.exists(), BUILDOZER_SPEC_PATH


def get_buildozer_config():
    config = ConfigParser(allow_no_value=True)
    config.read(BUILDOZER_SPEC_PATH)
    return config


def inject_boot_receiver_into_android_manifest_template():
    injected_chunk = '''<receiver android:name=".MyBootBroadcastReceiver" android:enabled="true" >
        <intent-filter><action android:name="android.intent.action.BOOT_COMPLETED" /></intent-filter>
    </receiver>'''

    config = get_buildozer_config()
    build_dir = Path(config.get("buildozer", "build_dir"))
    app_name = config.get("app", "package.name")
    full_manifest_tpl_path = build_dir.joinpath(
        "android/platform/build-armeabi-v7a/dists/%s__armeabi-v7a/templates/AndroidManifest.tmpl.xml" % app_name)

    current_tpl = full_manifest_tpl_path.read_text(encoding="utf8")
    if "MyBootBroadcastReceiver" not in current_tpl:
        logger.info("Injecting MyBootBroadcastReceiver into AndroidManifest.tmpl.xml")
        new_tpl = current_tpl.replace("</application>", injected_chunk + "\n    </application>" )
        if (new_tpl == current_tpl):
            raise RuntimeError("MyBootBroadcastReceiver injection into AndroidManifest.tmpl.xml failed")
        full_manifest_tpl_path.write_text(new_tpl, encoding="utf8")
    else:
        logger.info("MyBootBroadcastReceiver already present in AndroidManifest.tmpl.xml, skipping injection")


def before_apk_build(p4a_toolchain):
    inject_boot_receiver_into_android_manifest_template()


def after_apk_build(p4a_toolchain):
    pass


def before_apk_assemble(p4a_toolchain):
    pass


def after_apk_assemble(p4a_toolchain):
    pass
