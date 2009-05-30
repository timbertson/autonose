import logging
import sys
import os

logging.getLogger('test').setLevel(logging.DEBUG)
autonose_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
