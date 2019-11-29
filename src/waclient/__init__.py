
import sys
from logging import StreamHandler

#os.environ["KIVY_NO_CONSOLELOG"] = "1"  # If troubles
custom_kivy_stream_handler = StreamHandler()
sys._kivy_logging_handler = custom_kivy_stream_handler
