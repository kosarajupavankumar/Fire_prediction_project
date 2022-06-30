import logging
import os
from datetime import datetime

# create the directory if it doesn't exist
LOG_DIR = 'forest_logs'
CURRENT_TIME_STAMP = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
LOG_FILE_NAME = f'log_{CURRENT_TIME_STAMP}.log'

os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE_NAME)

logging.basicConfig(
    level=logging.DEBUG,
    filename=LOG_FILE_PATH,
    filemode='w',
    format="%(asctime)s %(levelname)s %(module)s => %(message)s ",
    datefmt="%d-%m-%Y %H:%M:%S",
)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
