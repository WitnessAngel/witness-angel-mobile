

def generate_crashdump(exc_info, target_url):

    import os
    import traceback
    import requests

    WACLIENT_TYPE = os.environ.get("WACLIENT_TYPE", "<NOTFOUND>")

    system_info = {"SOFTWARE": "WACLIENT", "WACLIENT_TYPE": WACLIENT_TYPE}

    try:
        from jnius import autoclass

        build = autoclass("android.os.Build")
        system_info["BRAND"] = build.BRAND
        system_info["DEVICE"] = build.DEVICE
        system_info["MANUFACTURER"] = build.MANUFACTURER
        system_info["MODEL"] = build.MODEL
        system_info["PRODUCT"] = build.PRODUCT

        version = autoclass("android.os.Build$VERSION")
        system_info["BASE_OS"] = version.BASE_OS
        system_info["CODENAME"] = version.CODENAME
        system_info["RELEASE"] = version.RELEASE
        system_info["SDK_INT"] = version.SDK_INT
    except ImportError:
        pass  # We're surely not on Android
    except Exception as exc:
        print("Could not gather android system info: %r" % exc)

    system_info_str = "\n".join(
        "%s: %s" % (k, v) for (k, v) in sorted(system_info.items())
    )

    main_exception_str = "\n".join(traceback.format_exception(*exc_info))

    full_report_str = """
    
SYSTEM INFO
===================
%s


EXCEPTION
===================
%s

""" % (
        system_info_str,
        main_exception_str,
    )

    requests.post(
        target_url, dict(crashdump=full_report_str)
    )  # If it fails, it fails...

    return full_report_str
