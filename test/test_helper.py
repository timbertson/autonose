import logging
import sys
import os

logging.getLogger('test').setLevel(logging.DEBUG)
autonose_root = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
if not autonose_root in sys.path:
	sys.path.insert(0, autonose_root)

