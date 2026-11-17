import logging
from pathlib import Path


def get_logger(name: str = "global_development_analytics") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        logger.addHandler(stream)
        Path("outputs/reports").mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler("outputs/reports/project.log", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger
