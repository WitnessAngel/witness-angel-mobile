
if __name__ == "__main__":
    from wacomponents.launcher import launch_app_or_service_with_crash_handler
    launch_app_or_service_with_crash_handler("waclient.application.background_service", client_type="SERVICE")
