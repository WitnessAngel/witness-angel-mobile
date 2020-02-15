import atexit
import subprocess
import sys

from kivy.logger import Logger as logger

from waclient.service_controller.base import ServiceControllerBase
from waclient.common_config import SRC_ROOT_DIR

class ServiceController(ServiceControllerBase):

    _subprocess = None

    def start_service(self):
        # "self._subprocess" might already exist but have crashed
        self._subprocess = subprocess.Popen(
            [sys.executable, "service.py"],
            shell=False,
            cwd=SRC_ROOT_DIR,
        )

    def stop_service(self):
        assert self._subprocess  # Else, workflow error
        self._send_message("/stop_server")
        try:
            self._subprocess.wait(timeout=40)
        except subprocess.TimeoutExpired:
            logger.error("Service subprocess didn't exit gracefully, we kill it now")
            self._subprocess.kill()
