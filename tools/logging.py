import logging
from logging.handlers import RotatingFileHandler
import sys,os

class Logging:
    def __init__(self):
        try:
            log_file = os.path.join(os.getenv("LOGGING_FOLDER"),os.getenv("LOGGING_FILE"))
            handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=10) # 5MB log files, 10 files
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger = logging.getLogger()
            logger.addHandler(handler)
            logger.setLevel(str.upper(os.getenv("LOGGING_LEVEL")))
        except Exception as e:
            print(f"An error occurred while setting up the logging: {e}")
            print(f"Check the .env file for the LOGGING_FOLDER, LOGGING_FILE, and LOGGING_LEVEL for accuracies.")
            sys.exit(1)
        self.logger = logger