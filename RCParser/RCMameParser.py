# -*- coding: utf-8 -*-

import ConfigParser
import os.path
import re

from lxml import etree

from RCUtils import *
from RCReport import RCReport
from RCGameParser import RCGameParser


class RCMameParser(RCGameParser):
	""" Parser pour système Mame """
	
	regex = ur'(?:set +(?P<set>\d+)|(?:rev(?:\.|ision)?|v(?:\.|er\.?|ersion)?) *(?P<version>(?:\.?[\w\d]+)*)|(?P<hack>bootleg|prototype|hack)|(?P<field>\w+))(?!\w)'
	
	def __init__(self, game_list, config, system, hyperpause=False, csv=None):
		super(RCMameParser, self).__init__(game_list, config, system, hyperpause=hyperpause, csv=csv)
		
		# Charge le fichier DAT et les fichiers de genres.
		dat_file  = config.get(system, 'dat_file')
		cat_files = load_cat_files(config.get(system, 'cat_files'))
		
		try:
			self.dat = etree.parse(dat_file)
		except IOError as e:
			raise RCException('Unable to open MAME .dat file (' + dat_file.decode('utf-8') + ').')
		
		self.cat = ConfigParser.ConfigParser(allow_no_value=True)
		
		self.cat.readfp(cat_files)
		cat_files.close()
	
	def _first_stage(self):
		report      = RCReport()
		ignore_cat  = self.config.get(self.system, 'ignore_cat').split(',')
		exclude_cat = self.config.get(self.system, 'exclude_cat').split(',')
		genres      = self.cat.sections()
		re_group    = re.compile(r'\((.+)\)')
		re_infos    = re.compile(RCMameParser.regex, re.IGNORECASE)
		
		# Parcours du fichier .dat
		for dat_game in self.dat.findall('game'):
			goto_next        = False
			game_source_name = dat_game.get('name')
			
			if game_source_name not in self.list:
				continue
			
			report.log('\t' + game_source_name, 2)
			
			# On ignore le jeu s'il il se trouve dans l'une des catégories à ignorer
			game_genre = None
			for genre in genres:
				if self.cat.has_option(genre, game_source_name):
					game_genre = genre
					
					if game_genre in ignore_cat:
						report.log('\t\t- Genre ignored (' + game_genre + ')', 3)
						goto_next = True
						break
					elif game_genre in exclude_cat:
						report.log('\t\t- Genre excluded (' + game_genre + ')', 3)
						self.move_games.append(game_source_name)
						goto_next = True
						break
					
					# On ne quitte pas la boucle, car un jeu peut avoir plusieurs genres.
			
			if goto_next:
				continue
			
			game_name = dat_game.find('description').text
			editor    = dat_game.find('manufacturer')
			year      = dat_game.find('year')
			set_num   = None
			country   = None
			version   = None
			hack      = None
			
			# On récupère avant tout le contenu dans chaque groupe de parenthèses.
			for group in re_group.findall(game_name):
				# On exécute la regex sur le groupe.
				for field in re_infos.finditer(group):
					temp_country = field.group('field')
					set_num      = set_num or field.group('set')
					version      = version or field.group('version')
					hack         = hack    or field.group('hack')
					
					if temp_country in self.countries or temp_country in self.exclude_countries:
						country = country or temp_country
			
			if set_num != None and int(set_num) > 1:
				report.log('\t\t- Not the first set (' + set_num + ')', 3)
				continue
			elif hack != None and self.config.get(self.system, 'only_legit'):
				report.log('\t\t- Not legit', 3)
				continue
			elif country == None and not self.config.get(self.system, 'allow_no_country'):
				report.log('\t\t- Country not found', 3)
				continue
			elif country != None and country in self.exclude_countries:
				report.log('\t\t- Excluded country (' + country + ')', 3)
				continue
			
			# Nettoyage du nom du jeu
			game_clean_name = clean_name(game_name)
			
			# On enregistre le jeu temporairement
			if game_clean_name not in self.temp_games:
				self.temp_games[game_clean_name] = []
			
			self.temp_games[game_clean_name].append({
				'original_name': game_source_name,
				'country':       country,
				'version':       1.0 if not version else norm_version(version),
				'editor':        editor.text if editor != None else 'Unknow',
				'year':          year.text if year != None else 'Unknow',
				'genre':         game_genre,
				'resume':        None,
				'note':          None,
				'rating':        None,
				'score':         1,
				'onlineData':    False
			})
			
			report.log('\t\t+ Preselected game. Clean name : ' + game_clean_name + ' (from "' + game_name + '")', 2)
		
		del self.dat
