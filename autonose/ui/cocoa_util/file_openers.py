import subprocess

class TextMateOpener(object):
	def __init__(self):
		self.tm_path = self._get_tm_path()
	
	def open(self, path, line):
		if not self.tm_path:
			return False
		subprocess.Popen([self.tm_path, path, '-wl', str(line)])
		return True
	
	def _get_tm_path(self):
		which_proc = subprocess.Popen(['which', 'mate'], stdout=subprocess.PIPE)
		(stdout, stderr) = which_proc.communicate()
		if which_proc.returncode != 0:
			return None
		return stdout.rstrip()

class DefaultOpener(object):
	def open(self, path, line):
		from Cocoa import NSWorkspace
		NSWorkspace.sharedWorkspace().openFile_(path)
		return True

all_openers = [TextMateOpener, DefaultOpener]
