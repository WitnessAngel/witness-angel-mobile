from logging import Handler


class CallbackHandler(Handler):

    def __init__(self, gui_console_callback):
        super().__init__()
        self._gui_console_callback = gui_console_callback

    def emit(self, record):
        try:
            msg = self.format(record)
            self._gui_console_callback(msg)
        except Exception as exc:
            print("Warning: exception in CallbackHandler when emitting record", record, "->", exc)


