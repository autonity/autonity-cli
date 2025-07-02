"""
Logging-related functions.
"""

import sys

# pylint: disable=global-statement

logging_enabled = False


def enable_logging() -> None:
    """
    Call to enable the log function.
    """
    global logging_enabled
    logging_enabled = True


def log(msg: str, no_newline: bool = False) -> None:
    """
    Log a message.  Currently just goes to stderr.
    """
    if logging_enabled:
        sys.stderr.write(msg)
        if not no_newline and msg[-1] != "\n":
            sys.stderr.write("\n")
