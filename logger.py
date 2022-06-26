import logging
import sys

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_DIR = "./logs/"

def get_console_handler():
   console_handler = logging.StreamHandler(sys.stdout)
   console_handler.setFormatter(FORMATTER)
   return console_handler

def get_file_handler(file_name):
   if file_name[:-4] != '.log':
      file_name += '.log'
   file_handler = logging.FileHandler(LOG_DIR + file_name)
   file_handler.setFormatter(FORMATTER)
   return file_handler

def get_logger(logger_name, file_name = "discord_bot.log"):
   logger = logging.getLogger(logger_name)
   logger.setLevel(logging.DEBUG)
   
   logger.addHandler(get_console_handler())
   logger.addHandler(get_file_handler(file_name))
   
   logger.propagate = False
   return logger