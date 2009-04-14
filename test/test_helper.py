import logging
import sys
import os

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
sniffles_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
