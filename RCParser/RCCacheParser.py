# -*- coding: utf-8 -*-

import codecs

from lxml import etree
from distutils.util import strtobool

from RCGameParser import RCGameParser

from RCUtils import RCException
from RCReport import RCReport

class RCCacheParser(RCGameParser):
	"""
		Parser pour les systèmes en cache, c'est à dire que le fichier BDD HyperSpin
		a déjà été généré.
		
		Utilisé pour les opérations post-génération, afin d'éviter de refaire tout le processus.
	"""
	
	def __init__(self, config, system, hyperpause=False, csv=None):
		super(RCCacheParser, self).__init__(None, config, system, hyperpause=hyperpause, csv=csv)
		
		self.use_cache = True
		self.generate  = False
	
	def _first_stage(self):
		""" Ouvre le fichier de base de données du système et enregistre les jeux. """
		
		report   = RCReport()
		
		try:
			database = codecs.open(self.system + '.xml', 'r', 'utf-8')
			xml      = etree.fromstring(database.read())
			
			database.close()
		except IOError as e:
			raise RCException('Unable to open database for "' + self.system + '".')
		
		
		for game in xml.findall('game'):
			manufacturer = game.find('manufacturer')
			year         = game.find('year')
			genre        = game.find('genre')
			resume       = game.find('resume')
			note         = game.find('note')
			rating       = game.find('rating')
			onlineData   = game.find('onlineData')
			
			self.games[game.find('description').text] = {
				'original_name': game.get('name'),
				'country':       None,
				'version':       None,
				'editor':        manufacturer.text if manufacturer != None else '',
				'year':          year.text         if year != None         else '',
				'genre':         genre.text        if genre != None        else '',
				'resume':        resume.text       if resume != None       else '',
				'note':          note.text         if note != None         else '',
				'rating':        rating.text       if rating != None       else '',
				'score':         None,
				'onlineData':    bool(strtobool(onlineData.text)) if onlineData != None else False
			}
