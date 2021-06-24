#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# common
import traceback


# %--start--
import pkg_resources
__version__ = '1.0.0.1'



# ==================================================
#                     LOGGING
# ==================================================
from .logger import getLogger
logger = getLogger(__name__)

import os
PROCESS_LEVEL = os.environ.get('PROCESS_LEVEL', 0)
os.environ['PROCESS_LEVEL'] = str(int(PROCESS_LEVEL)+1)



# ==================================================
#                      BASICS
# ==================================================
from .common import *
from .easy_basher import *
from .encrypter import *
from .file_based_db import *
from .inspecter import *
from .profiler import *
from .smart_json import *
from .strip_color_codes import *
from .node_simpler import *



# ==================================================
#                   OPTIONALS
# ==================================================
Skipped_Imports = {}


try:
    from .database import *
except Exception as e:
    Skipped_Imports['database'] = \
        traceback.format_exc().split('\n')

try:
    from .node import *
except Exception as e:
    Skipped_Imports['node'] = \
        traceback.format_exc().split('\n')

try:
    from .requests_v3 import *
except Exception as e:
    Skipped_Imports['requests_v3'] = \
        traceback.format_exc().split('\n')

try:
    from .speech_processing import *
except Exception as e:
    Skipped_Imports['speech_processing'] = \
        traceback.format_exc().split('\n')


if len(Skipped_Imports) > 0:
    logger.warning('Skipped_Imports:', Skipped_Imports)



# %--end--
del pkg_resources
