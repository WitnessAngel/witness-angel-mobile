from kivy.utils import platform


if platform == "android":
    from .android_service_controller import ServiceController
else:
    from .subprocess_service_controller import ServiceController
