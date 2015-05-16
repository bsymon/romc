# -*- coding: utf-8 -*-

import re

from urlparse import urlparse
from google import search
from bs4 import BeautifulSoup
from urllib2 import HTTPError

from RCUtils import RCException
from RCOnlineAPI import RCOnlineAPI

class RCIgnAPI(RCOnlineAPI):
	url = 'http://www.ign.com'
	
	def _search_game(self, game):
		"""
			Recher un lien vers un jeu sur IGN.com, via un recherche Google.
			La recherche à la syntaxe suivante : site:www.ign.com [Jeu] [Console]
		"""
		
		link = None
		
		try:
			site = urlparse(self.url).netloc
			
			# On récupère les 3 premiers liens afin d'être sûr d'avoir le lien vers le jeu.
			for result in search('site:%s %s %s' % (site, game, self.system), num=3, stop=1, pause=2):
				link = result if '.com/games/' in result else None
				
				if link:
					break
		except HTTPError as e:
			return -2
		
		return link
	
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
		
		try:
			resp      = self._request(url)
			html      = BeautifulSoup(resp)
			game_info = html.find(class_='gameInfo')
			
			# Sélection des champs qui nous intéresse.
			editor       = game_info.select('div[class="gameInfo-list"] > div:nth-of-type(2) > a')
			release_date = game_info.select('.gameInfo-list.leftColumn > div:first-of-type')
			genre        = game_info.select('div[class="gameInfo-list"] > div:nth-of-type(1) > a')
			rating       = html.select('.gameInfo-list.leftColumn > div:last-of-type > a')
			note         = html.select('.communityRating > .ratingValue')
			resume       = game_info.find('p')
			
			if len(editor) > 0:
				data['editor'] = editor[0].text.strip()
			if len(release_date) > 0:
				data['release_date'] = release_date[0].text.strip()[-4:]
			if len(genre) > 0:
				data['genre'] = genre[0].text.strip()
			if len(rating) > 0:
				data['rating'] = rating[0].text.replace(' for', '')
			if len(note) > 0:
				data['note'] = note[0].text.strip()
			if resume != None:
				data['resume'] = resume.text.strip()
		except RCException:
			pass
		
		return data
