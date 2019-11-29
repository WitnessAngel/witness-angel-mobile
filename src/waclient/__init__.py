
import sys, logging

#os.environ["KIVY_NO_CONSOLELOG"] = "1"  # If troubles
custom_kivy_stream_handler = logging.StreamHandler()
sys._kivy_logging_handler = custom_kivy_stream_handler

# For now allow EVERYTHING
logging.getLogger(None).setLevel(logging.DEBUG)
logging.disable(0)
