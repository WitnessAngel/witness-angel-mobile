import time
from waclient.service_controller import ServiceController

def test_service_controller():

    ctrl = ServiceController()

    try:

        ctrl.start_service()

        time.sleep(1)

        print(">>>>>", ctrl.ping())

        time.sleep(1)

        ctrl.stop_service()

    except:
        # Teardown cleanup
        if ctrl._subprocess:
            ctrl._subprocess.terminate()
        raise

