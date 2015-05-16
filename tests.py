# -*- coding: utf-8 -*-

from RCOnlineAPI.RCIgnAPI import RCIgnAPI

e = RCIgnAPI('Genesis', None)
link = e._search_game('Sonic The Hedgehog 1')

if link != None and link != -2:
	print e._get_data(link)
else:
	print 'Introuvable'
