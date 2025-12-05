import logging
import sys


def setup_logging():
    root = logging.getLogger()
    if root.handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    handler.setFormatter(formatter)
    root.setLevel(logging.INFO)
    root.addHandler(handler)


def get_logger(name: str):
    setup_logging()
    return logging.getLogger(name)
