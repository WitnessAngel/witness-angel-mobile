import os
import threading
from configparser import Error as ConfigParserError

from kivy.config import ConfigParser
from kivy.logger import Logger as logger
from oscpy.server import OSCThreadServer, ServerClass

from waclient.common_config import CONFIG_FILE


osc = OSCThreadServer(encoding="utf8")
# FIXME what happens if exception on remote OSC endpoint ?


@ServerClass
class BackgroundServer(object):

    _sock = None

    def __init__(self):
        logger.info("Starting service")
        self._sock = osc.listen(address='127.0.0.1', port=8765, family='inet', default=True)
        self._termination_event = threading.Event()
        logger.info("Service started")

    def _load_config(self, filename=CONFIG_FILE):
        config = ConfigParser(name='service')
        logger.info(f"Service loading config file {filename}")
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(filename)
            config.read(filename)  # Fails silently if file not found
        except ConfigParserError as exc:
            logger.error(f'Service: Ignored missing or corrupted config file {filename}, ignored ({exc!r})')
            raise
        logger.info(f"Config file {filename} loaded")
        return config

    @osc.address_method('/ping')
    def ping(self):
        logger.info("Ping successful!")
        config = self._load_config()
        print("Config:", config.getdefault("usersettings", "language", "ITALIANO"))

    @osc.address_method('/stop_server')
    def stop_server(self):
        logger.info("Stopping service")
        osc.stop_all()
        self._termination_event.set()
        logger.info("Service stopped")

    def join(self):
        """Wait for the termination of the background server."""
        self._termination_event.wait()

    def start_recording(self):
        config = self._load_config()

    def stop_recording(self):
        pass



'''
@osc.address(b'/address')
def callback(values):
    print("got values: {}".format(values))

sleep(1000)
osc.stop()


for i in range (10):
    print("-", end=" ")
'''


if __name__ == "__main__":
    logger.info("Starting service process")
    server = BackgroundServer()
    server.join()
    logger.info("Service process terminated ALMOST")
