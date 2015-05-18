# -*- coding: utf-8 -*-

import codecs
import os
import os.path
import ConfigParser
import importlib

from lxml import etree
from lxml.builder import E
from abc import ABCMeta, abstractmethod

from RCUtils import VERSION, RCException
from RCReport import RCReport
from RCOnlineAPI.RCJvcAPI import RCJvcAPI

HYPERPAUSE_DIR = 'HyperPause/'

class RCGameParser(object):
	__metaclass__ = ABCMeta
	
	""" Classe de base pour les parser. """
	
	regex = None
	
	def __init__(self, games_list, config, system, hyperpause=False):
		self.temp_games        = {}
		self.games             = {}
		self.list              = games_list or []
		self.config            = config
		self.system            = system
		self.hyperpause        = hyperpause
		self.excludes          = []
		self.move_games        = []
		self.move_temp_games   = False
		self.total_editions    = 0
		
		if config != None:
			self.countries         = config.get(system, 'country').split(',')[::-1]
			self.exclude_countries = config.get(system, 'exclude_country').split(',')
		
		self.use_cache         = False
	
	@abstractmethod
	def _first_stage(self):
		"""
			1er étape : pré-selectionne les jeux correspondants aux critères.
			
				- Le jeu doit être "legit" (pas de hack ou booleg), ou "only_legit" doit être = false.
				- Le pays du jeu doit se trouver dans "country", et ne pas être dans "exclude_country".
				- Si aucun pays trouvé, "allow_no_country doit être = true.
				
				Pour Mame :
					- le set du jeu doit être égal à 1.
				
				Pour les ROMS:
					- le dump doit être le meilleur possible (flags : ! ou fx où x est un numéro de version).
					- si aucun flags trouvés, le dump est considéré comme le meilleur.
			
			Il se peut qu'un même jeu existe en plusieurs versions (même nom, mais pays, version ou dump différent).
			Toutes les versions d'un jeu qui ont validé les critères sont pré-selectionnées.
		"""
		pass
	
	def _second_stage(self):
		"""
			2e étape : sélectionne la version d'un jeu qui correspond au mieux aux critères, parmis les différentes versions.
			
			Sélection le jeu par ordre de préférence du pays. Si indiqué, la version du dump doit être la plus récente.
			
			Avec ces critères, un score est calculé pour chaque version d'un jeu. La version qui a le score le plus élevé
			est sélectionnée.
		"""
		
		report = RCReport()
		
		for (game, editions) in self.temp_games.items():
			report.log('\t' + game + ' : ' + str(len(editions)) + ' declinations.', 2)
			
			highestScore = None
			lastScore    = 0
			
			self.total_editions += len(editions)
			
			# Calcule du score des éditions.
			if len(editions) > 1:
				for i, edition in enumerate(editions):
					score = edition['score']
					
					if edition['country'] != None:
						score += self.countries.index(edition['country'])
					else:
						score -= 1
					
					score += edition['version']
					
					if score >= lastScore:
						# On déplace le dernier jeu meilleur score, comme ce n'est plus lui.
						if highestScore != None and self.move_temp_games:
							self.move_games.append(editions[highestScore]['original_name'])
						
						lastScore    = score
						highestScore = i
					elif self.move_temp_games:
						# On déplace le jeu, car son score n'est pas le meilleur.
						self.move_games.append(edition['original_name'])
			else:
				highestScore = 0
			
			self.games[game] = editions[highestScore]
			
			report.log('\t\t>> Choice : ' + self.games[game]['original_name'], 2)
	
	def _build_database(self):
		"""
			Génère la base de données compatible HyperSpin.
		"""
		
		global VERSION
		
		db = E.menu(
			E.header(
				E.listname(self.system),
				E.listversion(VERSION),
				E.exportversion('Generated with RomCleaner (' + VERSION + ') - bsymon')
			)
		)
		
		for (game, infos) in self.games.items():
			game_tag = E.game(
				{ 'name': infos['original_name'], 'index': 'true', 'image': '1' },
				E.description(game),
				E.cloneof(''),
				E.crc(''),
				E.manufacturer(infos['editor'] or ''),
				E.year(infos['year'] or ''),
				E.genre(infos['genre'] or 'Unknow'),
				E.resume(infos['resume'] or ''),
				E.note(infos['note'] or ''),
				E.rating(infos['rating'] or ''),
				E.enabled('Yes')
			)
			
			db.append(game_tag)
		
		db_file = codecs.open(self.system + '.xml', 'w+', 'utf-8')
		
		db_file.write(etree.tostring(db, encoding='utf-8', pretty_print=True).decode('utf-8'))
		db_file.close()
	
	def _move_games(self):
		"""
			Déplace les jeux qui ne sont pas nécessaire, si "move_files" = true.
			
			Pour Mame: déplace les jeux avec un genre exlu.
			Pour les Roms : tous les jeux qui n'ont pas été sélectionné.
		"""
		
		if len(self.move_games) == 0:
			return
		elif not os.path.exists('_moved'):
			os.mkdir('_moved')
		
		exts = self.config.get(self.system, 'ext').split(',')
		
		for game in self.move_games:
			for ext in exts:
				file = game + '.' + ext
				if os.path.exists(file):
					os.rename(file, '_moved/' + file)
	
	def _online_data(self):
		"""
			Lance la recherche des informations en ligne, via l'API choisie dans "online_api".
		"""
		report   = RCReport()
		
		try:
			# Importe la bonne API.
			api_name = 'RC' + self.config.get(self.system, 'online_api').capitalize() + 'API'
			api_mod  = importlib.import_module('RCOnlineAPI.' + api_name)
			api      = getattr(api_mod, api_name)(self.system, self.config)
		except ImportError as e:
			report.log('\tOnline API "' + api_name + '" does not exist.')
			return
		except RCException as e:
			report.log('\t' + e.message)
			return
		
		report.log('\tUsing "' + api_name + '" API', 2)
		
		# On récupère les langues autorisées pour la recherche.
		lang = self.config.get(self.system, 'online_data_lang').split(',')
		
		for (game, infos) in self.games.items():
			if len(lang) > 0 and lang[0] != '' and infos['country'] not in lang:
				continue
			
			report.log('\tGetting data for ' + game, 2)
			
			data = api.search(game)
			
			if data == -1:
				report.log('\t\t>> Unable to find data.', 2)
			elif data == -2:
				report.log('\t\t>> HTTP Error, stop looking for online data.')
				break
			elif data != None:
				release_date = data['release_date']
				genre        = data['genre']
				editor       = data['editor']
				resume       = data['resume']
				note         = data['note']
				rating       = data['rating']
				
				# Je procède comme ceci afin d'éviter de perdre des données qui peuvent être déjà présentes
				infos['year']   = release_date or infos['year']
				infos['genre']  = genre        or infos['genre']
				infos['editor'] = editor       or infos['editor']
				infos['resume'] = resume       or infos['resume']
				infos['note']   = note         or infos['note']
				infos['rating'] = rating       or infos['rating']
	
	def _hyperpause(self):
		""" Génère un fichier INI pour HyperPause. """
		
		if not os.path.exists(HYPERPAUSE_DIR):
			os.mkdir(HYPERPAUSE_DIR)
		
		ini_file   = codecs.open(HYPERPAUSE_DIR + self.system + '.ini', 'w', 'utf-8')
		lines      = []
		
		for (game, infos) in self.games.items():
			section = infos['original_name']
			editor  = infos['editor'] or u''
			year    = infos['year'] or u''
			genre   = infos['genre'] or u''
			resume  = infos['resume'] or u''
			note    = infos['note'] or u''
			rating  = infos['rating'] or u''
			
			# Je n'utilise pas ConfigParser car celui-ci ne supporte pas l'unicode.
			lines.append('[%s]\n' % (section))
			lines.append('GoodName=%s\n' % (game))
			lines.append('Company=%s\n' % (editor))
			lines.append('Released=%s\n' % (year))
			lines.append('Genre=%s\n' % (genre))
			lines.append('Description=%s\n' % (resume))
			lines.append('Score=%s\n' % (note))
			lines.append('Rating=%s\n' % (rating))
			lines.append('\n')
		
		ini_file.writelines(lines)
		ini_file.close()
	
	def clean(self):
		""" Exécute les processus de nettoyage. """
		
		report = RCReport()
		
		report.log('FIRST STAGE : selecting games that respond to the criteria.')
		self._first_stage()
		
		if not self.use_cache:
			report.log('SECOND STAGE : choosing the best game.')
			self._second_stage()
			
			if self.config.get(self.system, 'move_files'):
				report.log('MOVING ' + str(len(self.move_games)) + ' GAMES')
				self._move_games()
			
			if self.config.get(self.system, 'online_data'):
				report.log('LOOKING FOR ONLINE DATA ...')
				self._online_data()
			
			report.log('BUILDING HYPERSPIN DATABASE')
			self._build_database()
		
		# On génère le fichier INI HyperPause si besoin.
		if self.hyperpause:
			report.log('GENERATING HYPERPAUSE INI FILE')
			self._hyperpause()
		
		# Rapport
		report.log('=============== REPORT ===============')
		report.log('\tInput : ' + str(len(self.list)) + ' games.')
		report.log('\tPreselected : ' + str(self.total_editions) + ' games.')
		report.log('\tOutput : ' + str(len(self.games)) + ' games.')
