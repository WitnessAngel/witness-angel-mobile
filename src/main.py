import os, sys


def launch_app_or_service(is_service):
    """
    Launcher used both for main app and service, depending on parameter.
    """

    # depending on cmd-line args or environments variables
    #is_service = (("PYTHON_SERVICE_ARGUMENT" in os.environ) or  # Android case
    #              ("service" in [p.lower() for p in sys.argv]))  # Subprocess case

    if is_service:
        os.environ["WACLIENT_TYPE"] = "SERVICE"
        from waclient.background_service import main  # NOW ONLY we trigger conf loading
    else:
        os.environ["WACLIENT_TYPE"] = "APPLICATION"
        from waclient.app import main  # NOW ONLY we trigger conf loading

    main()

if __name__ == "__main__":
    launch_app_or_service(is_service=False)
