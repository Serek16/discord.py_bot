import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_DIR = "./logs/"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler(file_name):
   file_handler = logging.FileHandler(LOG_DIR + file_name)
   file_handler.setFormatter(FORMATTER)
   return file_handler

def get_logger(logger_name, file_name = "discord_bot.log"):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG)
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler(file_name))
   # with this pattern, it's rarely necessary to propagate the error up to parent
   logger.propagate = False
   return logger