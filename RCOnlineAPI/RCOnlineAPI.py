# -*- coding: utf-8 -*-

import urllib
import urllib2

from abc import ABCMeta, abstractmethod

from RCReport import RCReport
from RCUtils import RCException

class RCOnlineAPI(object):
	__metaclass__ = ABCMeta
	
	url = None
	
	def __init__(self, system, config):
		self.system = system
		self.config = config
	
	@abstractmethod
	def _search_game(self, game):
		""" Renvoie le lien pour la prochaine requête dans self._get_data """
		pass
	
	@abstractmethod
	def _get_data(self, url):
		""" Récupère les données dans la page. """
		pass
	
	def search(self, game):
		"""
			Lance la recherche du jeu.
			
			Renvoi -1 si aucune info' trouvée, -2 si un erreur HTTP survient.
		"""
		
		report = RCReport()
		link   = self._search_game(game)
		data  = None
		
		if link == None:
			return -1
		elif link == -2:
			return -2
		else:
			data = self._get_data(link)
		
		return data
	
	def _request(self, url, method='GET', data=None, file=None):
		if data != None:
			data = urllib.urlencode(data)
			
			if method == 'GET':
				url += '?' + data
		
		try:
			req   = urllib2.Request(url, data if data != None and method == 'POST' else None)
			req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
			
			resp  = urllib2.urlopen(req)
			data  = resp.read()
			
			resp.close()
		except IOError as e:
			raise RCException('[Online data] Cannot connect to "' + url + '" : ' + e.message)
		
		return data
