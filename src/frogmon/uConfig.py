# uConfig.py
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from frogmon.uCommon import COM

class CONF():
	def __init__(self, filename):
		# Load configuration file
		try:
			self.config = ConfigParser(delimiters=('=', ), inline_comment_prefixes=('#'))
			self.config.optionxform = str
			self.confFileNM = filename
			self.config.read(self.confFileNM)
		except Exception as e:
			print("error : %s" % e)
	
	
	def reloadConfig(self):
		try:
			self.config.read(self.confFileNM)
			return 0
		except:
			print('Reload Error')
			return -1

			
	def readConfig(self, section, item, _def):
		try:
			return self.config[section].get(item, _def)
		except:
			print('section or item not found [%s:%s]' % (section,  item))
			return _def

	def writeConfig(self, section, item, val):
		self.config.set(section, item.lower(), val)
	
	def saveConfig(self):
		with open(self.confFileNM, 'w') as f:
			self.config.write(f)
			
	def isConfig(self, section):
		return self.config.has_section(section)
		#return config[section]
	
	def itemsConfig(self, section):
		return self.config[section].items()
		
	def itemRemove(self, section):
		self.config.remove_section(section)
		
	def sectionAdd(self, section):
		self.config.add_section(section)