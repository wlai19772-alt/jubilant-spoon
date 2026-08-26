"""
logger.py

这个模块负责记录程序运行日志。
日志用于跟踪启动、读取、AI 调用、保存、异常、结束等事件。
"""

import logging
from pathlib import Path


def create_logger(log_file: Path):
    """创建并返回日志记录器。"""
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("script_factory")
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)

    return logger
