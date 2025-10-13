import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

class BotLogger:
    def __init__(
        self,
        name: str = "bot",
        level: int = logging.INFO,
        log_to_console: bool = True,
        log_to_file: bool = False,
        log_dir: str = "logs",
        log_file: str = "bot.log",
        max_bytes: int = 5 * 1024 * 1024,  # 5 MB
        backup_count: int = 5
    ):


        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False  # щоб не дублювало повідомлення

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if log_to_file:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=Path(log_dir) / log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def get_logger(self):
        return self.logger


# Створюємо логер
logger = BotLogger(
    name="bot",
    level="INFO",
    log_to_console=True,
    log_to_file=True,
    log_dir="logs",
    log_file="bot.log",
    max_bytes=10 * 1024 * 1024,
    backup_count=5
).get_logger()