
import sys, logging

# For now allow EVERYTHING
logging.getLogger(None).setLevel(logging.INFO)
logging.disable(0)

custom_kivy_stream_handler = logging.StreamHandler()
sys._kivy_logging_handler = custom_kivy_stream_handler
