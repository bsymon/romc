# -*- coding: utf-8 -*-

import ConfigParser

from distutils.util import strtobool

from RCUtils import *

class RCConfig:
	def __init__(self):
		self._fields = {}
		
	def add_option(self, section, option, default, type):
		""" Ajoute une nouvelle option de configuration. """
		
		if section not in self._fields:
			self._fields[section] = {}
			
		if option in self._fields[section]:
			raise RCException(option + u' est déjà définie dans ' + section + '.')
		
		self._fields[section][option] = {
			'value': default,
			'type': type
		}

	def get(self, section, option):
		if not self._exists(section):
			raise RCException('La section de configuration "' + section + '" n\'existe pas.')
		elif not self._exists(section, option):
			raise RCException('L\'option de configuration "' + option + '" dans "' + section + '" n\'existe pas.')
		
		return self._fields[section][option]['value']
	
	def set(self, section, option, value):
		if not self._exists(section):
			raise RCException('La section de configuration "' + section + '" n\'existe pas.')
		elif not self._exists(section, option):
			raise RCException('L\'option de configuration "' + option + '" dans "' + section + '" n\'existe pas.')
		elif not isinstance(value, self._get_type(section, option)):
			raise RCException('La valeur de l\'option "' + section + '/' + option + '" n\'est pas du bon type.')
		
		self._fields[section][option]['value'] = value
	
	def read(self, config, only_section=None):
		""" Enregistre la configuration. """
		
		if not isinstance(config, ConfigParser.RawConfigParser):
			raise RCException('La configuration n\'est pas du bon type.')
		
		for section in config.sections():
			# On ignore la section si ce n'est pas celle qui nous intéresse.
			if only_section != None and section != only_section:
				continue
			
			for option in config.options(section):
				if not self._exists(section, option):
					raise RCException('L\'option "' + option + '" dans "' + section + '" dans le fichier de configuration n\'existe pas.')
				
				value = config.get(section, option)
				type  = self._get_type(section, option)
				
				# On converti la valeur brut (string) vers le bon type
				if type == bool:
					value = type(strtobool(value))
				else:
					value = type(value.encode('utf-8'))
				
				self.set(section, option, value)
	
	def write(self, filepath):
		file   = open(filepath, 'w+')
		config = ConfigParser.ConfigParser()
		
		# On construit la configuration
		for section in self._fields.keys():
			config.add_section(section)
			
			for option in self._fields[section].keys():
				config.set(section, option, self._fields[section][option]['value'])
			
		config.write(file)
		file.close()
	
	def _exists(self, section, option=None):
		if section not in self._fields:
			return False
		elif option != None and option not in self._fields[section]:
			return False
		
		return True
	
	def _get_type(self, section, option):
		if not self._exists(section, option):
			raise RCException('L\'option "' + section + '/' + option + '" n\'existe pas.')
		
		return self._fields[section][option]['type']
	
