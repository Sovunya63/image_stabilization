import logging
import sys
from pathlib import Path

LOGGER_NAME = "traffic_cam"

def init_logger(log_file="logs/traffic_cam.log"):
    logger = logging.getLogger(LOGGER_NAME)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s : %(message)s")
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

def get_logger(module_id=None) -> logging.Logger:
    base = init_logger()

    if not module_id or module_id == LOGGER_NAME:
        return base

    if module_id.startswith(f"{LOGGER_NAME}."):
        return logging.getLogger(module_id)

    return logging.getLogger(f"{LOGGER_NAME}.{module_id}")