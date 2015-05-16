# -*- coding: utf-8 -*-

import re
import string
from time import sleep

from urlparse import urlparse
from bs4 import BeautifulSoup, NavigableString
from urllib2 import HTTPError

from RCUtils import RCException
from RCOnlineAPI import RCOnlineAPI

class RCMobygamesAPI(RCOnlineAPI):
	"""
		Cette API est seulement utilisée par le système Mame.
		Pour avoir des informations pour d'autres support, utiliser
		les API Jvc ou Ign.
	"""
	
	url = 'http://www.mobygames.com'
	
	def _search_game(self, game):
		"""
			Recherche un jeu via le site Mobygames.com.
		"""
		
		# On prépare le nom du jeu afin d'être utilisé dans l'URL.
		autho = string.ascii_lowercase + string.digits + ' -'
		game  = ''.join([l for l in list(game.lower().translate(None, ':\'/*!&.').replace(' - ', '-').replace(' ', '-')) if l in autho])
		
		return self.url + '/game/arcade/' + game
	
	def _get_data(self, url):
		data = {
			'editor':       None,
			'release_date': None,
			'genre':        None,
			'rating':       None,
			'note':         None,
			'resume':       None,
			'image':        None
		}
		
		# TODO s'il ce n'est pas la 1er requête, faire une pause de x secondes
		
		try:
			resp = self._request(url)
			html = BeautifulSoup(resp)
			
			# Sélection des champs qui nous intéresse.
			editor       = html.select('#coreGameRelease a[href*="/company"]')
			release_date = html.select('#coreGameRelease a[href*="/release-info"]')
			genre        = html.select('#coreGameGenre a[href*="/genre"]')
			rating       = []
			note         = html.select('#coreGameScore .scoreHi')
			
			# Récupération du resume
			resume = ''
			
			for elem in html.find(class_='col-md-8').find('h2').next_siblings:
				if type(elem) != NavigableString and 'class' in elem.attrs and 'sideBarLinks' in elem['class']:
					break
				
				resume += elem.string or '\n'
			
			if len(editor) > 0:
				data['editor'] = editor[0].text.replace(u'\xa0', u' ') # Remplace les espace insécable
			if len(release_date) > 0:
				data['release_date'] = release_date[0].text
			if len(genre) > 0:
				data['genre'] = genre[0].text
			if len(rating) > 0:
				data['rating'] = rating.string
			if len(note) > 0:
				data['note'] = note[0].text.strip()
			
			data['resume'] = resume
		except RCException:
			pass
		
		return data
