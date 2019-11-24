import time
from waclient.service_controller import ServiceController

def test_service_controller():

    ctrl = ServiceController()

    try:

        ctrl.start()

        time.sleep(3)

        print(">>>>>", ctrl.ping())

        time.sleep(3)

        ctrl.stop()

    except:
        # Teardown cleanup
        if ctrl._subprocess:
            ctrl._subprocess.terminate()
        raise

