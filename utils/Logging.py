__author__ = 'heroico'

import logging

def configureLogging(level=5):
    logger = logging.getLogger()
    logger.setLevel(level)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(level)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)