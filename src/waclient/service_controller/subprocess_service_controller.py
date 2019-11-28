import sys, subprocess
from oscpy.client import OSCClient
from kivy.logger import Logger as logger


class ServiceController:

    _subprocess = None
    _osc = None

    def _send_message(self, address, *values):
        assert self._subprocess
        return self._osc.send_message(address, values=values)

    def start_service(self):
        assert not self._subprocess
        from waclient.common_config import ROOT_DIR
        self._subprocess = subprocess.Popen([sys.executable, "-m", "waclient.background_service"],
                                            shell=False, cwd=ROOT_DIR)
        self._osc = OSCClient(address='127.0.0.1', port=8765, encoding="utf8")
        # TODO - wait for remote server to be pingable?

    def ping(self):
        assert self._subprocess
        return self._send_message("/ping")

    def stop_service(self):
        assert self._subprocess
        self._send_message("/stop_server")
        try:
            self._subprocess.wait(timeout=30)
        except subprocess.TimeoutExpired:
            logger.error("Service subprocess didn't exit gracefully, we kill it now")
            self._subprocess.kill()

    def start_recording(self):
        self._send_message("/start_recording")

    def stop_recording(self):
        self._send_message("/stop_recording")
