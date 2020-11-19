
import os
if os.getenv("WACLIENT_ENABLE_TYPEGUARD"):
    from typeguard.importhook import install_import_hook
    install_import_hook('waclient')

from waguilib import kivy_presetup  # Trigger common setup
