import sys, subprocess

import atexit
from oscpy.client import OSCClient
from kivy.logger import Logger as logger

from waclient.utilities.osc import get_osc_client


class ServiceController:

    _subprocess = None
    _osc_client = None

    def start_service(self):
        assert not self._subprocess
        from waclient.common_config import ROOT_DIR
        self._subprocess = subprocess.Popen([sys.executable, "-m", "waclient.background_service"],
                                            shell=False, cwd=ROOT_DIR)
        self._osc_client = get_osc_client(to_master=False)
        # TODO - wait for remote server to be pingable?
        atexit.register(self.stop_service)  # Protection against ctrl-C

    def _send_message(self, address, *values):
        logger.debug("Message sent to service: %s", address)
        assert self._subprocess
        return self._osc_client.send_message(address, values=values)

    def ping(self):
        assert self._subprocess
        return self._send_message("/ping")

    def stop_service(self):
        assert self._subprocess
        self._send_message("/stop_server")
        try:
            self._subprocess.wait(timeout=40)
        except subprocess.TimeoutExpired:
            logger.error("Service subprocess didn't exit gracefully, we kill it now")
            self._subprocess.kill()

    def start_recording(self):
        self._send_message("/start_recording")

    def stop_recording(self):
        self._send_message("/stop_recording")

    def broadcast_recording_state(self):
        self._send_message("/broadcast_recording_state")

    def attempt_container_decryption(self, container_filepath):
        self._send_message("/attempt_container_decryption", container_filepath)


