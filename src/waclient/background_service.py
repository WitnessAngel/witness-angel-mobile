import contextlib
import os
import threading
from configparser import Error as ConfigParserError

from decorator import decorator
from kivy.config import ConfigParser
from kivy.logger import Logger as logger
from oscpy.server import OSCThreadServer, ServerClass

from waclient.common_config import CONFIG_FILE
from waclient.recording_toolchain import build_recording_toolchain, start_recording_toolchain, stop_recording_toolchain

osc = OSCThreadServer(encoding="utf8")
# FIXME what happens if exception on remote OSC endpoint ? CRASH!!
# TODO add custom "local escrow resolver"
# TODO add exception swallowers, and logging pushed to frontend app (if present)


@decorator
def swallow_exception(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        try:
            logger.error(f"Caught unhandled exception in call of function {f!r}: {exc!r}")
        except Exception as exc2:
            print("Beware, service callback {f!r} and logging system are both broken: {exc2!r}")


@ServerClass
class BackgroundServer(object):

    """
    The background server automatically starts when service script is launched.

    It must be stopped gracefully with a call to "/stop_server", so that current recordings can be properly stored.

    While the server is alive, recordings can be started and stopped several times without problem.
    """
    _sock = None

    _recording_toolchain = None

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
            config.read(str(filename))  # Fails silently if file not found
        except ConfigParserError as exc:
            logger.error(f'Service: Ignored missing or corrupted config file {filename}, ignored ({exc!r})')
            raise
        logger.info(f"Config file {filename} loaded")
        return config

    @osc.address_method('/ping')
    @swallow_exception
    def ping(self):
        logger.info("Ping successful!")

    @osc.address_method('/start_recording')
    @swallow_exception
    def start_recording(self):
        #print("Config:", config.getdefault("usersettings", "language", "ITALIANO"))
        if self.is_recording:
            logger.warning("Ignoring call to service.start_recording(), since recording is already started")
            return
        logger.info("Starting recording")
        if not self._recording_toolchain:
            config = self._load_config()
            self._recording_toolchain = build_recording_toolchain(config)
        start_recording_toolchain(self._recording_toolchain)
        logger.info("Recording started")

    @property
    def is_recording(self):
        return self._recording_toolchain and self._recording_toolchain["sensors_manager"].is_running

    @osc.address_method('/stop_recording')
    @swallow_exception
    def stop_recording(self):
        if not self.is_recording:
            logger.warning("Ignoring call to service.stop_recording(), since recording is already stopped")
            return
        logger.info("Stopping recording")
        stop_recording_toolchain(self._recording_toolchain)
        logger.info("Recording stopped")

    @osc.address_method('/stop_server')
    @swallow_exception
    def stop_server(self):
        logger.info("Stopping service")

        if self.is_recording:
            logger.info("Recording is in progress, we stop it as part of service shutdown")
            self.stop_recording()

        osc.stop_all()
        self._termination_event.set()
        logger.info("Service stopped")

    @swallow_exception
    def join(self):
        """
        Wait for the termination of the background server
        (meant for use by the main thread of the service process).
        """
        self._termination_event.wait()


def main():
    logger.info("Service process launches")
    server = BackgroundServer()
    server.join()
    logger.info("Service process exits")


if __name__ == "__main__":
    main()
