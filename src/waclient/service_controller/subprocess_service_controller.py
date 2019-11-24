import sys, subprocess
from oscpy.client import OSCClient



class ServiceController:

    _subprocess = None
    _osc = None

    def _send_message(self, address, *values):
        assert self._subprocess
        return self._osc.send_message(address, values=values)

    def start(self):
        assert not self._subprocess
        from waclient import ROOT_DIR
        self._subprocess = subprocess.Popen([sys.executable, "-m", "waclient.background_service"],
                                            shell=False, cwd=ROOT_DIR)
        self._osc = OSCClient(address='127.0.0.1', port=8765, encoding="utf8")

    def ping(self):
        assert self._subprocess
        return self._send_message("/ping")

    def stop(self):
        assert self._subprocess
        self._send_message("/stop_server")
        self._subprocess.wait(timeout=10)
