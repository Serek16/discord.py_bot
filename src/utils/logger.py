import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_DIR = "./logs/"

if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)


def _get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def _get_file_handler(file_name):
    if file_name[:-4] != '.log':
        file_name += '.log'
    file_handler = TimedRotatingFileHandler(LOG_DIR + file_name, when='D', interval=1, backupCount=7)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name, file_name="discord_bot.log"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    logger.addHandler(_get_console_handler())
    logger.addHandler(_get_file_handler(file_name))

    logger.propagate = False
    return logger
