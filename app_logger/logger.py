import logging as lg
from datetime import datetime
import os


ROOT_DIR = os.getcwd()
CURRENT_TIME_STAMP = f"{datetime.now().strftime('%Y-%m-%d')}"
LOG_DIR= os.path.join(ROOT_DIR,  "app_logs")


def App_Logger(Logger_Name, Log_Level="DEBUG" , Stream_Level="INFO"):
    
    FILE_NAME = f"{CURRENT_TIME_STAMP}_{Logger_Name}_logs.log"
    LOG_FILE = os.path.join(LOG_DIR, FILE_NAME)
    os.makedirs(LOG_DIR, exist_ok=True)
    logger = lg.getLogger(Logger_Name)
    logger.setLevel(lg.Log_Level)

    # Creating Formatters
    format = lg.Formatter('%(asctime)s:\t %(levelname)s:\t:%(message)s')
    # Creating Handlers
    file_handler = lg.FileHandler(LOG_FILE)

    # Adding Formatters to Handlers
    file_handler.setFormatter(format)
    # Adding Handlers to logger
    logger.addHandler(file_handler)
    
    stream_handler = lg.StreamHandler()
    stream_handler.setLevel(lg.Stream_Level)
    logger.addHandler(stream_handler)
    return logger