import os
from pathlib import Path

if __name__ == "__main__":
    os.environ["WA_SERVICE_SCRIPT"] = Path(__file__).resolve().parent.joinpath("service.py")
    from waguilib.safe_launcher import launch_app_or_service
    launch_app_or_service("waclient.app", client_type="APPLICATION")
