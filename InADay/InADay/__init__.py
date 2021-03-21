import logging
from datetime import date
import os

from InADay import settings

today = date.today().strftime("%Y-%m-%d")

increment = 0
while os.path.exists(os.path.join(settings.LOG_FILE_DIR, f'{settings.BOT_NAME}_{today}_{increment}.log')):
    increment += 1

LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
filename = os.path.join(settings.LOG_FILE_DIR, f'{settings.BOT_NAME}_{today}_{increment}.log')

logging.basicConfig(filename=filename,
                    level=logging.DEBUG,
                    format=LOG_FORMAT,
                    datefmt='%m-%d-%Y %H:%M:%S',
                    filemode='w')
