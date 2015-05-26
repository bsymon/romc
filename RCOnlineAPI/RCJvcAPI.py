# -*- coding: utf-8 -*-

import re

from urlparse import urlparse
from google import search
from bs4 import BeautifulSoup
from urllib2 import HTTPError

from RCUtils import RCException
from RCOnlineAPI import RCOnlineAPI


class RCJvcAPI(RCOnlineAPI):
	url = 'http://www.jeuxvideo.com'
	
	def _search_game(self, game):
		"""
			Recher un lien vers un jeu sur Jeuxvideo.com, via un recherche Google.
			La recherche à la syntaxe suivante : site:www.jeuxvideo.com [Jeu] [Console]
		"""
		
		link = None
		
		try:
			site = urlparse(self.url).netloc
			
			# On récupère les 2 premiers liens afin d'être sûr d'avoir le lien vers le jeu.
			for result in search('site:%s %s %s' % (site, game, self.system), num=2, stop=1, pause=5):
				link = result if '/jeux/' in result else None
				
				if link:
					break
		except HTTPError as e:
			return -2
		
		return link
	
	def _get_data(self, url):
		rating_re = re.compile('\+ ?(3|7|12|16|18) ?ans') # Regex pour trouver le classement PEGI du jeu.
		data      = {
			'editor':       None,
			'release_date': None,
			'genre':        None,
			'rating':       None,
			'note':         None,
			'resume':       None,
			'image':        None
		}
		
		try:
			resp     = self._request(url)
			html     = BeautifulSoup(resp)
			techlist = html.find(class_='resume-tech-list')
			
			# Si "techlist" vaut None, c'est que ce n'est pas une fiche de jeu.
			if techlist != None:
				# Sélection des champs qui nous intéresse.
				editor       = techlist.select('li[itemprop="creator"] span[itemprop="name"]')
				release_date = techlist.select('li[itemprop="creator"] + li > span')
				genre        = techlist.select('span[itemprop="genre"] > *')
				rating       = techlist.find(text=rating_re)
				note         = html.select('div.hit-note-g')
				resume       = html.select('span[itemprop="description"]')
				
				if len(editor) > 0:
					data['editor'] = editor[0].text
				if len(release_date) > 0:
					data['release_date'] = release_date[0]['content'][0:4]
				if len(genre) > 0:
					data['genre'] = genre[0].text
				if rating != None:
					data['rating'] = rating.string
				if len(note) > 0:
					data['note'] = note[0].text.strip()
				if len(resume) > 0:
					data['resume'] = resume[0].text
				
				if self.config.get(self.system, 'download_covers'):
					image = html.select('span.recto-jaquette.actif > span:first-element-of')
					
					if len(image) > 0:
						img_url       = 'http:' + image[0]['data-selector']
						img_ext       = img_url[img_url.rindex('.'):]
						data['image'] = { 'file': self._request(img_url, file=True), 'ext': img_ext }
			else:
				return -1
		except RCException:
			pass
		
		return data
	
	def _decrypt_link(self, crypted):
		base16 = '0A12B34C56D78E9F'
		url    = ''
		
		j = 0
		while j < len(crypted):
			ch   = base16.index(crypted[j])
			cl   = base16.index(crypted[j + 1])
			url += chr((ch * 16) + cl)
			
			j += 2
		
		return url
