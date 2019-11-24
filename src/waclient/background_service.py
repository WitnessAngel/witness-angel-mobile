import threading

from oscpy.server import OSCThreadServer, ServerClass
from time import sleep


osc = OSCThreadServer(encoding="utf8")


@ServerClass
class BackgroundServer(object):

    _sock = None

    def __init__(self):
        print("Starting server!")
        self._sock = osc.listen(address='127.0.0.1', port=8765, family='inet', default=True)
        self._termination_event = threading.Event()
        print("Started server!")

    @osc.address_method('/ping')
    def ping(self, *args):
        print("Ping successful!")

    @osc.address_method('/stop_server')
    def stop_server(self):
        print("Stopping server!")
        osc.stop_all()
        self._termination_event.set()

    def join(self):
        """Wait for the termination of the background server."""
        print("Waiting for server execution!")
        self._termination_event.wait()
        print("Server terminated!")


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
    server = BackgroundServer()
    server.join()
