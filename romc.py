# -*- coding: utf-8 -*-

import argparse
import codecs
import ConfigParser
import httplib
import os
import os.path
import sys

from RCUtils import *
from RCReport import RCReport
from RCConfig import RCConfig
from RCParser.RCMameParser import RCMameParser
from RCParser.RCRomParser import RCRomParser
from RCParser.RCCacheParser import RCCacheParser

def main(args=sys.argv):
	cmd         = init_cmd_line()
	system      = cmd.system
	hyperpause  = cmd.hyperpause
	cache       = cmd.cache
	config      = RCConfig()
	base_config = RCConfig()
	
	try:
		config_file   = codecs.open('config.ini', 'r', 'utf-8')
		config_parser = ConfigParser.ConfigParser()
		
		# Parsage de la config'
		config_parser.readfp(config_file)
		config_file.close()
		
		# On vérifie si le systeme est present dans la conf'
		if system not in config_parser.sections():
			raise RCException('"' + system + '" is not a registered system.')
		elif system == BASE_CONFIG_SECTION:
			raise RCException('"' + system + '" is not a valid system name.')
		
		# Montage de la config
		config.add_option(system, 'dir',              '',    str)
		config.add_option(system, 'ext',              '',    str)
		config.add_option(system, 'country',          '',    str)
		config.add_option(system, 'exclude_country',  '',    str)
		config.add_option(system, 'allow_no_country', True,  bool)
		config.add_option(system, 'only_legit',       True,  bool)
		config.add_option(system, 'special',          True,  bool)
		config.add_option(system, 'flags',            '',    str)
		config.add_option(system, 'online_data',      False, bool)
		config.add_option(system, 'online_data_lang', '',    str)
		config.add_option(system, 'online_api',       '',    str)
		config.add_option(system, 'is_mame',          False, bool)
		config.add_option(system, 'dat_file',         '',    str)
		config.add_option(system, 'cat_files',        '',    str)
		config.add_option(system, 'ignore_cat',       '',    str)
		config.add_option(system, 'exclude_cat',      '',    str)
		config.add_option(system, 'move_files',       False,  bool)
		
		base_config.add_option(BASE_CONFIG_SECTION, 'log_process', True, bool)
		base_config.add_option(BASE_CONFIG_SECTION, 'log_level',   1,    int)
		base_config.add_option(BASE_CONFIG_SECTION, 'log_file',    '',   str)
		
		# Synchro du fichier avec la config
		config.read(config_parser, system)
		base_config.read(config_parser, BASE_CONFIG_SECTION)
		
		# On charge le dossier de jeux
		cwd   = os.path.normpath(config.get(system, 'dir').decode('utf-8'))
		games = load_games_dir(cwd, config.get(system, 'ext')) # NOTE peut-être ne pas charger si use_cache
		
		os.chdir(cwd)
		
		if cache:
			cleaner = RCCacheParser(config, system, hyperpause=hyperpause)
		elif config.get(system, 'is_mame'):
			cleaner = RCMameParser(games, config, system, hyperpause=hyperpause)
		else:
			cleaner = RCRomParser(games, config, system, hyperpause=hyperpause)
		
		report = RCReport(system, base_config)
		report.log('ROMC : start cleaning "' + system + '"')
		report.log('======================================')
		
		cleaner.clean()
		
		report.log('======================================')
		report.log('Done !')
	except IOError as e:
		print 'ERROR : Unable to open the configuration file.'
	except RCException as e:
		print 'ERROR : ' + e.message.encode('utf-8')
	

def init_cmd_line():
	parser = argparse.ArgumentParser(prog='romc.py', description='Clean roms and Mame games, and generate a database compatible with HyperSpin Front-End.')
	
	parser.add_argument('system', type=str, metavar='SYSTEM', help='The system to clean.')
	parser.add_argument('-p', '--hpause', dest='hyperpause', action='store_true', help='Generate HyperPause game info INI.')
	parser.add_argument('-c', '--cache', dest='cache', action='store_true', help='Whether use or not a generated database for SYSTEM.')
	
	return parser.parse_args()

if __name__ == '__main__':
	main();
