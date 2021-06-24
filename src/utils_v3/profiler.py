#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import os
import time


# logger
from .logger import getLogger
logger = getLogger(__name__)



def lap(env_var='UTILS_V3__TIMER', note=''):

    current_time = time.time()

    logger.green(
        'Lapped({}):'.format(note),
        current_time - float(os.getenv('UTILS_V3__TIMER', current_time)),
    )

    os.environ['UTILS_V3__TIMER'] = str(current_time)
