import shutil
import sys, os
from configparser import ConfigParser
from pathlib import Path
import logging
from shutil import SameFileError

logger = logging.getLogger('p4a')

THIS_DIR = Path(__file__).absolute().parent
BUILDOZER_SPEC_PATH = THIS_DIR.parent.joinpath("buildozer.spec")
assert BUILDOZER_SPEC_PATH.exists(), BUILDOZER_SPEC_PATH


def get_buildozer_config():
    config = ConfigParser(allow_no_value=True)
    config.read(BUILDOZER_SPEC_PATH)
    return config


def get_app_build_directory():

    config = get_buildozer_config()
    build_dir = Path(config.get("buildozer", "build_dir"))
    app_name = config.get("app", "package.name")
    app_build_dir = build_dir.joinpath(
        "android/platform/build-armeabi-v7a/dists/%s__armeabi-v7a/" % app_name)
    return app_build_dir


def inject_boot_receiver_into_android_manifest_template():

    injected_chunk = '''
    <receiver android:name="org.whitemirror.witnessangeldemo.MyBootBroadcastReceiver" android:exported="true" android:enabled="true">
        <intent-filter>
            <action android:name="android.intent.action.BOOT_COMPLETED"/>
            <action android:name="android.intent.action.QUICKBOOT_POWEROFF" />
            <action android:name="android.intent.action.QUICKBOOT_POWERON" />
            <!--For HTC devices-->
            <action android:name="com.htc.intent.action.QUICKBOOT_POWEROFF"/>
            <action android:name="com.htc.intent.action.QUICKBOOT_POWERON"/>
            <category android:name="android.intent.category.DEFAULT"/>
        </intent-filter>
    </receiver>
    '''

    app_build_directory = get_app_build_directory()
    full_manifest_tpl_path = app_build_directory.joinpath("templates/AndroidManifest.tmpl.xml")

    current_tpl = full_manifest_tpl_path.read_text(encoding="utf8")
    if "MyBootBroadcastReceiver" not in current_tpl:
        logger.info("Injecting MyBootBroadcastReceiver into AndroidManifest.tmpl.xml")
        new_tpl = current_tpl.replace("</application>", injected_chunk + "\n    </application>" )
        if (new_tpl == current_tpl):
            raise RuntimeError("MyBootBroadcastReceiver injection into AndroidManifest.tmpl.xml failed")
        full_manifest_tpl_path.write_text(new_tpl, encoding="utf8")
    else:
        logger.info("MyBootBroadcastReceiver already present in AndroidManifest.tmpl.xml, skipping injection")


def add_java_boot_service_file_to_build():

    app_build_directory = get_app_build_directory()
    target_file = app_build_directory.joinpath("src/main/java/org/whitemirror/witnessangeldemo")

    logger.info("Copying MyBootBroadcastReceiver.java into app java libs")
    shutil.copy(
        THIS_DIR / "MyBootBroadcastReceiver.java",
        target_file / "MyBootBroadcastReceiver.java"
    )



def before_apk_build(p4a_toolchain):
    inject_boot_receiver_into_android_manifest_template()
    add_java_boot_service_file_to_build()


def after_apk_build(p4a_toolchain):
    pass


def before_apk_assemble(p4a_toolchain):
    pass


def after_apk_assemble(p4a_toolchain):
    pass
