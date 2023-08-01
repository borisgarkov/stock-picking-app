import logging
from time import time


logging.basicConfig(
    filename='stock_logger.txt',
    filemode='w',
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y-%m-%d %I:%M:%S%p",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def log(func):
    def inner(*args, **kwargs):
        logger.info(f'{func.__name__} is starting')

        start = time()
        result = func(*args, **kwargs)
        end = time()

        logger.info(f'{func.__name__} took {end - start} to complete')

        return result
    return inner
