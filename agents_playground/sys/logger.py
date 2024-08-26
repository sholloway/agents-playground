from enum import IntEnum
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
    formatter = logging.Formatter("{asctime} {name} {levelname} {filename}:{lineno} {message}", style="{")

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

class LoggingLevel(IntEnum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.CRITICAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARNING
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

from collections import defaultdict
from dataclasses import dataclass

@dataclass
class TableStats:
    num_cols: int
    col_widths: list[int]
    table_width: int

class LogTableError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

LOG_TABLE_NONUNIFORM_ERR = 'The table is not uniform in size. All rows must have the same number of columns.'

def _default_to_zero() -> int:
    return 0

def _stringify(rows: list[list]) -> list[list[str]]:
    """Convert a 2D list to a 2D list of strings"""
    return [[str(value) for value in row] for row in rows]

def _determine_table_stats(rows: list[list[str]], separator = " ") -> TableStats:
    # 1. Find the size of first row.
    num_cols: int = len(rows[0])

    # 2. Are they all the same length?
    same_size = [num_cols == len(row) for row in rows]
    all_same_sizes = all(same_size)
    if not all_same_sizes:
        raise LogTableError(LOG_TABLE_NONUNIFORM_ERR)
    
    # 3. Find the minimum width of each column
    column_sizes = defaultdict(_default_to_zero)
    for row in rows:
        for col, value in enumerate(row):
            current_size = column_sizes[col]
            column_sizes[col] = max(current_size, len(value))
    sorted_items = sorted(column_sizes.items(), key=lambda i: i[0])
    col_widths = [item[1] for item in sorted_items]

    # Find the width of the table.
    separator_len = len(separator)
    table_width = (separator_len * (len(col_widths) - 1)) + sum(col_widths)

    return TableStats(num_cols, col_widths, table_width)

def _build_table_format(col_widths: list[int], separator = " ") -> str:
    """Construct a string formatter."""
    formatter = "| " + separator.join(["{:<"+str(width)+"}" for width in col_widths]) + " |"
    return formatter

def _format_table_rows(
    table_stats: TableStats, 
    formatter: str, 
    header: list[str], 
    rows: list[list[str]]
) -> list[str]:
    table: list[str] = []
    hor_boarder = "-" * (table_stats.table_width + 4)
    table.append(hor_boarder)
    table.append(formatter.format(*header))
    table.append(hor_boarder)
    formatted_rows = [formatter.format(*row) for row in rows]
    table.extend(formatted_rows)
    table.append(hor_boarder)
    return table

def build_data_table(
    header: list[str],
    rows: list[list]) -> list[str]: 
    separator = " | "
    rows_of_strings: list[list[str]] = _stringify(rows)
    table_stats: TableStats = _determine_table_stats([header] + rows_of_strings, separator)
    formatter: str = _build_table_format(table_stats.col_widths, separator)
    return _format_table_rows(table_stats, formatter, header, rows_of_strings)
     

def log_table(
    header: list[str],
    rows: list[list], 
    message: str,  
    level: LoggingLevel=LoggingLevel.INFO
) -> None:
    table = build_data_table(header, rows)
    table.insert(0, message)
    log_msg = "\n".join(table)
    logger = get_default_logger()
    logger.log(level=level, msg=log_msg)