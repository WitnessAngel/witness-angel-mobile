import os
import socket
from pathlib import Path

from kivy.logger import Logger as logger
from kivy.utils import platform

# TODO factorize and use unix socks when possible
from oscpy.client import OSCClient
from oscpy.server import OSCThreadServer

from waclient.common_config import INTERNAL_APP_ROOT


def _osc_default_handler(address, *values):
    logger.warning(
        "Unknown OSC address %s called (arguments %s)", address, list(values)
    )


def _get_osc_socket_options(socket_index):
    if platform == "win":
        socket_options = dict(
            address="127.0.0.1", port=6420 + socket_index, family="inet"
        )
    else:
        socket_file = INTERNAL_APP_ROOT.joinpath(".witnessangel%d.sock" % socket_index)
        socket_options = dict(address=str(socket_file), port=None, family="unix")
    return socket_options


def get_osc_server(is_master=True):
    """
    Get the OSC server for the app (master) or service (slave)
    """
    server = OSCThreadServer(
        encoding="utf8", default_handler=_osc_default_handler
    )  # This launches a DAEMON thread!

    socket_index = 0 if is_master else 1
    socket_name = "application" if is_master else "service"
    socket_options = _get_osc_socket_options(socket_index=socket_index)

    def starter_callback():
        logger.info(
            "Binding OSC server of %s process to socket %s"
            % (socket_name, socket_options)
        )
        if socket_options["family"] == "unix":
            socket_file = Path(socket_options["address"])
            if socket_file.exists():
                socket_file.unlink()  # Else "Address already in use" error occurs when listening!
        server.listen(default=True, **socket_options)

    return server, starter_callback


def get_osc_client(to_master=True):

    socket_index = 0 if to_master else 1
    socket_options = _get_osc_socket_options(socket_index=socket_index)

    socket_family = socket_options.pop("family")
    sock = socket.socket(
        socket.AF_UNIX if socket_family == "unix" else socket.AF_INET, socket.SOCK_DGRAM
    )
    socket_options["sock"] = sock
    client = OSCClient(encoding="utf8", **socket_options)

    return client
