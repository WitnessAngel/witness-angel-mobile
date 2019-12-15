import sys, subprocess

import atexit
from kivy.logger import Logger as logger

from waclient.service_controller.base import ServiceControllerBase


class ServiceController(ServiceControllerBase):

    _subprocess = None

    def start_service(self):
        assert not self._subprocess
        from waclient.common_config import ROOT_DIR

        self._subprocess = subprocess.Popen(
            [sys.executable, "-m", "waclient.background_service"],
            shell=False,
            cwd=ROOT_DIR,
        )
        # TODO - wait for remote server to be pingable?
        atexit.register(self.stop_service)  # Protection against brutal ctrl-C

    def stop_service(self):
        assert self._subprocess  # Else, workflow error
        atexit.unregister(self.stop_service)  # No need anymore
        self._send_message("/stop_server")
        try:
            self._subprocess.wait(timeout=40)
        except subprocess.TimeoutExpired:
            logger.error("Service subprocess didn't exit gracefully, we kill it now")
            self._subprocess.kill()
