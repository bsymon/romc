# -*- coding: utf-8 -*-

import codecs

from lxml import etree
from distutils.util import strtobool

from RCGameParser import RCGameParser
from RCMameParser import RCMameParser
from RCRomParser import RCRomParser

from RCUtils import *
from RCReport import RCReport

class RCCacheParser(RCGameParser):
	"""
		Parser pour les systèmes en cache, c'est à dire que le fichier BDD HyperSpin
		a déjà été généré.
		
		Utilisé pour les opérations post-génération, afin d'éviter de refaire tout le processus.
	"""
	
	def __init__(self, games_list, config, system, hyperpause=False, csv=None, strl=0, strl_suffix='', csv_no_info_str=''):
		super(RCCacheParser, self).__init__(games_list, config, system, hyperpause=hyperpause, csv=csv, strl=strl, strl_suffix=strl_suffix, csv_no_info_str=csv_no_info_str)
		
		self.use_cache = True
		self.generate  = False
	
	def _first_stage(self):
		""" Ouvre le fichier de base de données du système et enregistre les jeux. """
		
		report  = RCReport()
		renamed = {}
		
		try:
			database = codecs.open(self.system + '.xml', 'r', 'utf-8')
			xml      = etree.fromstring(database.read())
			
			database.close()
		except IOError as e:
			raise RCException('Unable to open database for "' + self.system + '".')
		
		
		for game in xml.findall('game'):
			name         = game.find('description').text
			manufacturer = game.find('manufacturer')
			year         = game.find('year')
			genre        = game.find('genre')
			resume       = game.find('resume')
			note         = game.find('note')
			rating       = game.find('rating')
			onlineData   = game.find('onlineData')
			
			filename  = game.get('name')
			game_name = clean_filename(filename)
			
			# On vérifie si le jeu est nouveau
			if filename in self.list:
				# Le jeu a été renomé, on le sauvegarde temporairement
				if filename != game_name:
					renamed[filename] = self.list[filename]
				
				del(self.list[filename])
			# Le jeu a été supprimé. On ne l'ajoute pas dans la BDD
			else:
				report.log('\tDeleted game : "' + name + '"')
				self.generate = True
				continue
			
			self.games[name] = {
				'original_name': filename,
				'game_name':     game_name,
				'country':       None,
				'version':       None,
				'editor':        manufacturer.text if manufacturer != None else '',
				'year':          year.text         if year != None         else '',
				'genre':         genre.text        if genre != None        else '',
				'resume':        resume.text       if resume != None       else '',
				'note':          note.text         if note != None         else '',
				'rating':        rating.text       if rating != None       else '',
				'score':         None,
				'onlineData':    { 'state': bool(strtobool(onlineData.get('state'))) if onlineData != None else False }
			}
			
			for api in onlineData:
				self.games[name]['onlineData'][api.tag] = bool(strtobool(api.text))
		
		# On ajoute les jeux qui n'étaient pas présent de la BDD
		if len(self.list) > 0:
			parser = None
			
			if self.config.get(self.system, 'is_mame'):
				parser = RCMameParser(self.list, self.config, self.system, self.hyperpause, self.csv, self.strl, self.strl_suffix, self.csv_no_info_str)
			else:
				parser = RCRomParser(self.list, self.config, self.system, self.hyperpause, self.csv, self.strl, self.strl_suffix, self.csv_no_info_str)
			
			report.log('ADDING NEW GAMES TO THE DATABASE ...')
			
			report.log('NEW GAMES : First stage ...')
			parser._first_stage()
			
			report.log('NEW GAMES : Second stage ...')
			parser._second_stage()
			
			# On fusionne les nouveaux jeux à la BDD
			self.games.update(parser.games)
		
		# On ajoute à nouveaux les jeux renommés, afin que les fichiers associés soient renommés aussi
		self.list.update(renamed)
