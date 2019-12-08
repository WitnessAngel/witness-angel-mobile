from waclient.common_config import SERVICE_CLASS, ACTIVITY_CLASS, SERVICE_START_ARGUMENT
from waclient.service_controller.base import ServiceControllerBase


class ServiceController(ServiceControllerBase):

    def start_service(self):
        from jnius import autoclass
        self._service = autoclass(SERVICE_CLASS)
        self._activity = autoclass(ACTIVITY_CLASS).mActivity
        self._service.start(self._activity, SERVICE_START_ARGUMENT)

    def stop_service(self):
        self._send_message("/stop_server")
        ## TODO AFTER DELAY ?? self._service.stop(self._activity)
