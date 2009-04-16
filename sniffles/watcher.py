import nose
import sys
import logging
import os

from shared import file_util
import scanner

log = logging.getLogger(__name__)
debug = log.debug

class Watcher(nose.plugins.Plugin):
	name = 'sniffles'
	score = 800
	
	def __init__(self, state=None):
		super(self.__class__, self).__init__()
		if state is None:
			state = scanner.scan()
		self.state = state
		self.files_to_run = state.affected
		debug(self.files_to_run)

	def wantFile(self, filename):
		debug("want file %s? %s" % (filename, "NO" if (file_util.relative(filename) not in self.files_to_run) else "if you like..."))
		if file_util.relative(filename) not in self.files_to_run:
			return False

	def  finalize(self, result):
		scanner.save()

