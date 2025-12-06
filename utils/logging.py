"""
Structured logging for the Howitzer security testing tool.

Provides a simple logging abstraction with different log levels,
replacing scattered print() statements throughout the codebase.
"""

import sys
from typing import Optional


class HowitzerLogger:
    """
    Structured logger for Howitzer with multiple log levels.

    Supports info, verbose, warning, and error logging with optional
    verbose mode that can be toggled on/off.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the logger.

        Args:
            verbose: Enable verbose logging output
        """
        self.verbose = verbose

    def info(self, message: str) -> None:
        """
        Log informational message to stdout.

        Args:
            message: The message to log
        """
        print(f"[INFO] {message}")

    def verbose_log(self, message: str) -> None:
        """
        Log verbose message to stdout (only if verbose mode enabled).

        Args:
            message: The message to log
        """
        if self.verbose:
            print(f"[VERBOSE] {message}")

    def warning(self, message: str) -> None:
        """
        Log warning message to stderr.

        Args:
            message: The warning message to log
        """
        print(f"[WARNING] {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        """
        Log error message to stderr.

        Args:
            message: The error message to log
        """
        print(f"[ERROR] {message}", file=sys.stderr)

    def success(self, message: str) -> None:
        """
        Log success message to stdout.

        Args:
            message: The success message to log
        """
        print(f"[SUCCESS] {message}")

    def debug(self, message: str) -> None:
        """
        Log debug message to stdout (only if verbose mode enabled).

        Alias for verbose_log() for convenience.

        Args:
            message: The debug message to log
        """
        self.verbose_log(message)

    def separator(self, char: str = "=", length: int = 80) -> None:
        """
        Print a separator line.

        Args:
            char: Character to use for separator
            length: Length of separator line
        """
        print(char * length)

    def banner(self, message: str, char: str = "=") -> None:
        """
        Print a banner with message.

        Args:
            message: Message to display in banner
            char: Character to use for banner border
        """
        self.separator(char)
        print(message)
        self.separator(char)


# Global logger instance (can be configured from main)
_global_logger: Optional[HowitzerLogger] = None


def get_logger() -> HowitzerLogger:
    """
    Get the global logger instance.

    Returns:
        The global HowitzerLogger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = HowitzerLogger()
    return _global_logger


def set_logger(logger: HowitzerLogger) -> None:
    """
    Set the global logger instance.

    Args:
        logger: The logger instance to use globally
    """
    global _global_logger
    _global_logger = logger
