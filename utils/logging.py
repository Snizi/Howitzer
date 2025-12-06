
import sys
from typing import Optional


class HowitzerLogger:

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def info(self, message: str) -> None:
        print(f"[INFO] {message}")

    def verbose_log(self, message: str) -> None:
        if self.verbose:
            print(f"[VERBOSE] {message}")

    def warning(self, message: str) -> None:
        print(f"[WARNING] {message}", file=sys.stderr)

    def error(self, message: str) -> None:
        print(f"[ERROR] {message}", file=sys.stderr)

    def success(self, message: str) -> None:
        print(f"[SUCCESS] {message}")

    def debug(self, message: str) -> None:
        self.verbose_log(message)

    def separator(self, char: str = "=", length: int = 80) -> None:
        print(char * length)

    def banner(self, message: str, char: str = "=") -> None:
        self.separator(char)
        print(message)
        self.separator(char)


_global_logger: Optional[HowitzerLogger] = None


def get_logger() -> HowitzerLogger:
    global _global_logger
    if _global_logger is None:
        _global_logger = HowitzerLogger()
    return _global_logger


def set_logger(logger: HowitzerLogger) -> None:
    global _global_logger
    _global_logger = logger
