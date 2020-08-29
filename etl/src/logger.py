import os
import logging
import time

LOGS_DIR = os.getenv('LOGS_DIR', './logs')
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(f'{LOGS_DIR}/{time.strftime("%Y%m%d-%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger()