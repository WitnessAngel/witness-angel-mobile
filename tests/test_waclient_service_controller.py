import time, os

from _waclient_test_utilities import purge_test_cryptainers, list_test_cryptainers
from waguilib.service_control import ServiceController


def _test_service_controller(
    sleep_time_s,
    recording_iterations=1,
    skip_stop_recording=False,
    kill_instead_of_stop_service=False,
    expected_return_code=0,
    expected_cryptainers_count=1,
):

    ctrl = ServiceController()
    purge_test_cryptainers()

    try:

        ctrl.start_service()

        time.sleep(1)

        stats = ctrl.ping()
        print("OSC stats received through ping() call:", stats)

        for i in range(recording_iterations):
            print("=======NEW RECORDING ITERATION IN TESTS=======")
            ctrl.start_recording(env="test")
            ctrl.start_recording(env="test")  # Ignored

            time.sleep(sleep_time_s)

            if not skip_stop_recording:
                ctrl.stop_recording()
                ctrl.stop_recording()  # Ignored

            time.sleep(sleep_time_s)

        if kill_instead_of_stop_service:
            ctrl._subprocess.terminate()
        else:
            ctrl.stop_service()

        termination_sleep_s = 40 if skip_stop_recording else 2
        time.sleep(termination_sleep_s)  # Let the process terminate
        assert ctrl._subprocess.poll() == expected_return_code

    except Exception:
        # Teardown cleanup, in case of error
        if ctrl._subprocess and ctrl._subprocess.poll() is None:
            ctrl._subprocess.terminate()
        raise

    cryptainer_filepaths = list_test_cryptainers()
    assert len(cryptainer_filepaths) == expected_cryptainers_count
    assert all(
        os.stat(cryptainer_filepath).st_size > 100
        for cryptainer_filepath in cryptainer_filepaths
    )


def test_service_controller_simple_case():
    _test_service_controller(sleep_time_s=2)


def test_service_controller_multiple_recordings():
    _test_service_controller(
        sleep_time_s=2, recording_iterations=2, expected_cryptainers_count=2
    )


def test_service_controller_automatic_recording_shutdown():
    # Recordings are force-stopped before process exits
    _test_service_controller(sleep_time_s=2, skip_stop_recording=True)


def test_service_controller_violent_shutdown():
    # When brutally killing
    _test_service_controller(
        sleep_time_s=2,
        skip_stop_recording=True,
        kill_instead_of_stop_service=True,
        expected_return_code=1,
        expected_cryptainers_count=0,
    )
