import logging
import os
from datetime import datetime

def setup_logger(name="RequestLogger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Check if handlers already exist to avoid duplication
    if not logger.handlers:
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Create file handler
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        today = datetime.now().strftime("%Y%m%d")
        fh = logging.FileHandler(f"{log_dir}/bot_{today}.log")
        fh.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger
