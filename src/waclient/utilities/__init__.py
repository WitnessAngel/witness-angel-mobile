from decorator import decorator
from kivy.logger import Logger as logger


@decorator
def swallow_exception(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Exception as exc:
        try:
            logger.error(f"Caught unhandled exception in call of function {f!r}: {exc!r}")
        except Exception as exc2:
            print("Beware, service callback {f!r} and logging system are both broken: {exc2!r}")
