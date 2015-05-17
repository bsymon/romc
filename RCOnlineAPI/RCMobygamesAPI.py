# -*- coding: utf-8 -*-

import re
import string
from time import sleep

from urlparse import urlparse
from bs4 import BeautifulSoup, NavigableString
from urllib2 import HTTPError

from RCReport import RCReport
from RCUtils import RCException
from RCOnlineAPI import RCOnlineAPI

REQUEST_SLEEP_TIME = 2

class RCMobygamesAPI(RCOnlineAPI):
	"""
		Cette API est seulement utilisée par le système Mame.
		Pour avoir des informations pour d'autres support, utiliser
		les API Jvc ou Ign.
	"""
	
	url = 'http://www.mobygames.com'
	
	def __init__(self, system, config):
		super(RCMobygamesAPI, self).__init__(system, config)
		
		if not config.get(system, 'is_mame'):
			raise RCException('Mobygames API can only be used by Mame.')
		
		self.is_first_request = True
	
	def _search_game(self, game):
		"""
			Recherche un jeu via le site Mobygames.com.
		"""
		
		# On prépare le nom du jeu afin d'être utilisé dans l'URL.
		autho = string.ascii_lowercase + string.digits + ' -'
		game  = ''.join([l for l in list(game.lower().translate(None, ':\'/*!&.').replace(' - ', '-').replace(' ', '-')) if l in autho])
		
		return self.url + '/game/arcade/' + game
	
	def _get_data(self, url):
		report = RCReport()
		data   = {
			'editor':       None,
			'release_date': None,
			'genre':        None,
			'rating':       None,
			'note':         None,
			'resume':       None,
			'image':        None
		}
		
		if not self.is_first_request:
			sleep(REQUEST_SLEEP_TIME)
		
		try:
			resp = self._request(url)
			html = BeautifulSoup(resp)
			
			# Sélection des champs qui nous intéresse.
			note = html.select('#coreGameScore .scoreHi')
			
			# Récupération du resume
			desc_block = html.find(class_='col-md-8')
			resume     = ''
			
			if desc_block != None:
				for elem in desc_block.find('h2').next_siblings:
					if type(elem) != NavigableString and 'class' in elem.attrs and 'sideBarLinks' in elem['class']:
						break
					
					resume += elem.string or '\n'
				data['resume'] = resume
			
			if len(note) > 0:
				data['note'] = note[0].text.strip()
		except RCException:
			pass
		
		self.is_first_request = False
		
		return data
