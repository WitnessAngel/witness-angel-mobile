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
    
    <service android:name="org.whitemirror.witnessangeldemo.MyBootBroadcastReceiver"
                     android:process=":service_bootbroadcastreceiver" />
                     
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
    target_dir = app_build_directory.joinpath("src/main/java/org/whitemirror/witnessangeldemo")

    if not target_dir.exists():  # FIXME put before APK assemble instead???
        logger.warning("Couldn't copy MyBootBroadcastReceiver.java since target dir %s doesn't exist (yet), maybe on next build?" % target_dir)

    logger.info("Copying MyBootBroadcastReceiver.java into app java libs")
    shutil.copy(
        THIS_DIR / "MyBootBroadcastReceiver.java",
            target_dir / "MyBootBroadcastReceiver.java"
    )


def complete_apk_blacklist():
    """Needed until Buildozer supports "--blacklist" option."""

    # FIXME USE android.blacklist_src instead of HOOK!!!!!!

    blacklist_additions = ["# custom entries added by buildozer_hooks.py", "Crypto/SelfTest/*"]
    logger.info("Completing blacklist.txt with entries %s" % str(blacklist_additions))

    app_build_directory = get_app_build_directory()

    blacklist_file = app_build_directory / "blacklist.txt"

    existing_entries = blacklist_file.read_text(encoding="utf8").splitlines()

    for blacklist_addition in blacklist_additions:
        if blacklist_addition not in existing_entries:
            existing_entries.append(blacklist_addition)

    blacklist_file.write_text("\n".join(existing_entries), encoding="utf8")


def before_apk_build(p4a_toolchain):
    ###inject_boot_receiver_into_android_manifest_template()
    ###add_java_boot_service_file_to_build()
    complete_apk_blacklist()


def after_apk_build(p4a_toolchain):
    pass


def before_apk_assemble(p4a_toolchain):
    pass

def after_apk_assemble(p4a_toolchain):
    pass
