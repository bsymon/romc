#  -*- coding: utf-8 -*-

import codecs

from RCUtils import BASE_CONFIG_SECTION

class _RCReport(object):
	def __init__(self, system, config):
		self.system   = system
		self.config   = config
		self.file     = None
		
		file = config.get(BASE_CONFIG_SECTION, 'log_file')
		
		if file != '':
			self.file = codecs.open(file, 'w', 'utf-8')
	
	def log(self, what, level=1):
		if self.config.get(BASE_CONFIG_SECTION, 'log_process') and level <= self.config.get(BASE_CONFIG_SECTION, 'log_level'):
			print what
		
		if self.file != None:
			self.file.write(what + '\n')
	
_RCReport_instance = None
def RCReport(*args, **kargs):
	global _RCReport_instance
	if not _RCReport_instance:
		_RCReport_instance = _RCReport(*args, **kargs)
	return _RCReport_instance
