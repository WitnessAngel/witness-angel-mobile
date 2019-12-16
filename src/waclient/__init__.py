

try:
    # MUST BE ROBUST DUE TO NEED FOR RESILIENT "CRASH HANDLER" ACCESS #

    import logging
    import sys
    custom_kivy_stream_handler = logging.StreamHandler()
    sys._kivy_logging_handler = custom_kivy_stream_handler
    from kivy.logger import Logger as logger  # Trigger init of Kivy logging
    del logger

    # Finish ugly monkey-patching by Kivy
    assert logging.getLogger("kivy") is logging.root
    logging.Logger.root = logging.root
    logging.Logger.manager.root = logging.root

    # For now allow EVERYTHING
    logging.root.setLevel(logging.DEBUG)
    logging.disable(0)

    # import logging_tree
    # logging_tree.printout()
except Exception as exc:
    print(">>>>>>>> FAILED INITIALIZATION OF WACLIENT LOGGING: %r" % exc)
