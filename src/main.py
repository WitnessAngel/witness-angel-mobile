import os
from pathlib import Path

if __name__ == "__main__":
    os.environ["WA_SERVICE_SCRIPT"] = Path(__file__).resolve().parent.joinpath("service.py")
    from wacomponents.launcher import launch_app_or_service_with_crash_handler
    launch_app_or_service_with_crash_handler("waclient.app", client_type="APPLICATION")
