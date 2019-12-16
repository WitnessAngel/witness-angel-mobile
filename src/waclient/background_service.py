import io
import logging
import os
import tarfile
import threading
from configparser import Error as ConfigParserError

from kivy.config import ConfigParser
from kivy.logger import Logger as logger

from oscpy.server import ServerClass
from waclient.common_config import (
    APP_CONFIG_FILE,
    INTERNAL_KEYS_DIR,
    EXTERNAL_DATA_EXPORTS_DIR,
    get_encryption_conf,
)
from waclient.recording_toolchain import (
    build_recording_toolchain,
    start_recording_toolchain,
    stop_recording_toolchain,
)
from waclient.utilities.logging import CallbackHandler
from waclient.utilities.misc import safe_catch_unhandled_exception
from waclient.utilities.osc import get_osc_server, get_osc_client
from wacryptolib.container import decrypt_data_from_container
from wacryptolib.key_storage import FilesystemKeyStorage
from wacryptolib.utilities import load_from_json_file

# os.environ["KIVY_NO_CONSOLELOG"] = "1"  # IMPORTANT

osc, osc_starter_callback = get_osc_server(is_master=False)

# FIXME what happens if exception on remote OSC endpoint ? CRASH!!
# TODO add custom "local escrow resolver"
# TODO add exception swallowers, and logging pushed to frontend app (if present)


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
        logger.info("Starting service")  # Will not be sent to App (too early)
        osc_starter_callback()  # Opens server port
        self._osc_client = get_osc_client(to_master=True)
        logging.getLogger(None).addHandler(
            CallbackHandler(self._remote_logging_callback)
        )
        self._termination_event = threading.Event()
        self._local_key_storage = FilesystemKeyStorage(keys_dir=INTERNAL_KEYS_DIR)
        logger.info("Service started")

    def _remote_logging_callback(self, msg):
        return self._send_message("/log_output", "Service: " + msg)

    def _send_message(self, address, *values):
        print("Message sent from service to app: %s", address)
        try:
            return self._osc_client.send_message(address, values=values)
        except OSError as exc:
            # NO LOGGING HERE, else it would loop due to custom logging handler
            print(
                "{SERVICE} Could not send osc message %s%s to app: %r"
                % (address, values, exc)
            )
            return

    def _load_config(self, filename=APP_CONFIG_FILE):
        logger.info(f"(Re)loading config file {filename}")
        config = (
            ConfigParser()
        )  # No NAME here, sicne named parsers must be Singletons in process!
        try:
            if not os.path.exists(filename):
                raise FileNotFoundError(filename)
            config.read(str(filename))  # Fails silently if file not found
        except ConfigParserError as exc:
            logger.error(
                f"Service: Ignored missing or corrupted config file {filename}, ignored ({exc!r})"
            )
            raise
        # logger.info(f"Config file {filename} loaded")
        return config

    @osc.address_method("/ping")
    @safe_catch_unhandled_exception
    def ping(self):
        logger.info("Ping successful!")
        self._send_message("/log_output", "Pong")

    @osc.address_method("/start_recording")
    @safe_catch_unhandled_exception
    def start_recording(self, env=None):
        try:
            encryption_conf = get_encryption_conf(env)
            if self.is_recording:
                logger.warning(
                    "Ignoring call to service.start_recording(), since recording is already started"
                )
                return
            logger.info("Starting recording")
            if not self._recording_toolchain:
                config = self._load_config()
                self._recording_toolchain = build_recording_toolchain(
                    config,
                    local_key_storage=self._local_key_storage,
                    encryption_conf=encryption_conf,
                )
            start_recording_toolchain(self._recording_toolchain)
            logger.info("Recording started")
        finally:
            self.broadcast_recording_state()  # Even on error

    @property
    def is_recording(self):
        return bool(
            self._recording_toolchain
            and self._recording_toolchain["sensors_manager"].is_running
        )

    @osc.address_method("/broadcast_recording_state")
    @safe_catch_unhandled_exception
    def broadcast_recording_state(self):
        logger.info(
            "Broadcasting service state (is_recording=%s)" % self.is_recording
        )  # TODO make this DEBUG
        self._send_message("/receive_recording_state", self.is_recording)

    @osc.address_method("/stop_recording")
    @safe_catch_unhandled_exception
    def stop_recording(self):
        if not self.is_recording:
            logger.warning(
                "Ignoring call to service.stop_recording(), since recording is already stopped"
            )
            return
        logger.info("Stopping recording")
        try:
            stop_recording_toolchain(self._recording_toolchain)
            logger.info("Recording stopped")
        finally:  # Trigger all this even if container flushing failed
            self._recording_toolchain = (
                None
            )  # Will force a reload of config on next recording
            self.broadcast_recording_state()

    @osc.address_method("/attempt_container_decryption")
    @safe_catch_unhandled_exception
    def attempt_container_decryption(self, container_filepath):
        logger.info("Decryption requested for container %s", container_filepath)
        target_directory = EXTERNAL_DATA_EXPORTS_DIR.joinpath(
            os.path.basename(container_filepath)
        )
        target_directory.mkdir(
            exist_ok=True
        )  # Double exports would replace colliding files
        container = load_from_json_file(container_filepath)
        tarfile_bytes = decrypt_data_from_container(
            container, local_key_storage=self._local_key_storage
        )
        tarfile_bytesio = io.BytesIO(tarfile_bytes)
        tarfile_obj = tarfile.open(
            mode="r", fileobj=tarfile_bytesio  # TODO add gzip support here one day
        )
        # Beware, as root on unix systems it would apply chown/chmod
        tarfile_obj.extractall(target_directory)
        logger.info(
            "Container content was successfully decrypted into folder %s",
            target_directory,
        )

    @osc.address_method("/stop_server")
    @safe_catch_unhandled_exception
    def stop_server(self):
        logger.info("Stopping service")

        if self.is_recording:
            logger.info(
                "Recording is in progress, we stop it as part of service shutdown"
            )
            self.stop_recording()

        osc.stop_all()
        self._termination_event.set()
        logger.info("Service stopped")

    @safe_catch_unhandled_exception
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
