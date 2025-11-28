import logging
from logging.handlers import TimedRotatingFileHandler

def initialize_logger():
    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    timed_rotating_handler = TimedRotatingFileHandler('logs/sacm.log', when='midnight', interval=1, backupCount=5)
    console_handler = logging.StreamHandler()

    timed_rotating_handler.setLevel(logging.DEBUG)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s - %(message)s')
    timed_rotating_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(timed_rotating_handler)
    logger.addHandler(console_handler)