import functools
import logging
import os
import sys

DEFAULT_LOGGER_NAME = "agent_playground"
LOG_FILE_NAME = "agents_playground.log"
UTF_8_ENCODING = "utf-8"


def get_default_logger() -> logging.Logger:
    return logging.getLogger(DEFAULT_LOGGER_NAME)

def log_call(func):
    """
    A decorator that logs that a function or method was called.
    """
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        logger: logging.Logger = get_default_logger()
        logger.info(f"{func.__qualname__}")
        return func(*args, **kwargs)
    return _wrapper


# Based On: https://ankitbko.github.io/blog/2021/04/logging-in-python/
def log(_func=None):
    """
    Logging Decorator

    Uses:
    No logger is passed. get_default_logger() is called.
    @log()
    some_function()
    """

    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_default_logger()
            try:
                # Pull the function's args out.
                args_repr = [repr(a) for a in args]
                # If there is a dict passed, then pull those args as well.
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                # Build up the function's signature.
                signature = ", ".join(args_repr + kwargs_repr)
                logger.debug(f"function {func.__name__} called with args {signature}")
            except Exception as ee:
                raise ee

            try:
                # Actually run the decorated function.
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logger.exception(
                    f"Exception raised in {func.__name__}. exception: {str(e)}"
                )
                raise e

        return wrapper

    if _func is None:
        return decorator_log
    else:
        return decorator_log(_func)


def setup_logging(loglevel: str) -> logging.Logger:
    """
    Setup the default logger for the project. Logs to both the console and a file.
    """
    # 1. Get the numeric value of the log level provided on the command line.
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)

    # 2. Create the logger.
    logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    logger.setLevel(numeric_level)

    # 3. Create a stream handler for STDOUT/STDERR
    ch = logging.StreamHandler()
    ch.setLevel(numeric_level)  # TODO: Probably set this to just be errors.

    # 4. Create a file handler for the log file.
    fh = logging.FileHandler(filename=LOG_FILE_NAME, mode="w", encoding=UTF_8_ENCODING)
    fh.setLevel(numeric_level)

    # 5. Create a formatter
    formatter = logging.Formatter("{asctime} {name} {levelname} {message}", style="{")

    # 6. Add formatter to the handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # 7. Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    # Log platform details.
    impl = sys.implementation
    logger.info(f"Starting the logger for {DEFAULT_LOGGER_NAME}")
    logger.info(
        f"Python Version: {impl.name} {impl.version.major}.{impl.version.minor}.{impl.version.micro}-{impl.version.releaselevel}"
    )
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"OS: {os.name}")

    return logger
