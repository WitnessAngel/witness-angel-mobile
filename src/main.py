import os, sys

def launch_app_or_service(is_service):
    """
    Launcher used both for main app and service, depending on parameter.
    """

    # depending on cmd-line args or environments variables
    #is_service = (("PYTHON_SERVICE_ARGUMENT" in os.environ) or  # Android case
    #              ("service" in [p.lower() for p in sys.argv]))  # Subprocess case

    try:
        if is_service:
            os.environ["WACLIENT_TYPE"] = "SERVICE"
            from waclient.background_service import main  # NOW ONLY we trigger conf loading
        else:
            os.environ["WACLIENT_TYPE"] = "APPLICATION"
            from waclient.app import main  # NOW ONLY we trigger conf loading

        main()
    except Exception:
        if 'ANDROID_ARGUMENT' not in os.environ:
            raise  # Dev should not be impacted
        print(">> FATAL ERROR IN WACLIENT LAUNCHER (is_service=%s) ON MOBILE PLATFORM, SENDING CRASH REPORT <<"
              % is_service)
        exc_info = sys.exc_info()
        target_url = "https://waescrow.prolifik.net/crashdumps/"  # Can't access common config safely here
        from waclient.utilities.crashdumps import generate_and_send_crashdump  # Should be mostly safe to import
        report = generate_and_send_crashdump(exc_info=exc_info, target_url=target_url)
        print(report)  # Not to stderr for now, since it is hooked by Kivy logging

if __name__ == "__main__":
    launch_app_or_service(is_service=False)
