# -*- coding: utf-8 -*-

import os.path
import codecs
import StringIO
import string

from glob import glob

VERSION             = '1.0'
BASE_CONFIG_SECTION = 'BaseConfig'

def load_games_dir(dir, exts):
	""" Charge les fichiers jeux dans le dossier dir, avec les extensions exts """
	
	if not os.path.exists(dir):
		raise RCException('"' + dir + '" does not exist.')
	if not os.path.isdir(dir):
		raise RCException('"' + dir + '" is not a valid directory.')
	
	# Si aucune extension n'a été renseignée dans la config, on charge tous les fichiers.
	if exts.strip() == '':
		exts = '*'
	else:
		exts   = exts.replace('.', '').split(',')
	
	files  = []
	
	for ext in exts:
		# On supprime le chemin et l'extension pour ne garder que le nom
		files.extend([os.path.basename(x)[0:-(len(ext) + 1)] for x in glob(os.path.normpath(dir + '/*.' + ext))])
	
	return files

def load_cat_files(cat_files):
	"""
		Charge le/les fichiers de catégories Mame.
		Si il y a plusieurs fichiers, ils sont fusionnés.
	"""
	
	cat_files = cat_files.split(',')
	merged    = StringIO.StringIO()
	
	# On ouvre tous les fichiers.
	for file in cat_files:
		file = os.path.normpath(file.decode('utf-8'))
		
		if not os.path.isfile(file):
			raise RCException('"' + file + '" is not a file.')
		elif not os.path.exists(file):
			raise RCException('Categories file "' + file + '" does not exist.')
		
		genre = os.path.basename(file)
		file  = codecs.open(file, 'r', 'utf-8')
		
		merged.write(file.read().replace('ROOT_FOLDER', genre[:genre.index('.')]) + '\n')
		file.close()
	
	merged.flush()
	merged.seek(0)
	
	return merged

def norm_version(version):
	"""
		Normalise un numéro de version vers un type float.
	"""
	
	if version == None:
		return 1.0
	
	r = version
	
	for l in list(r):
		ll = l.lower()
		if ll in string.lowercase:
			r = r.replace(l, str(ord(ll) - 96))
	
	# S'il y a plus de 1 point dans la chaine, on supprime tous les autres.
	if r.count('.') > 1:
		dot1 = r.index('.') + 1
		r    = r[:dot1] + r[dot1:].replace('.', '')
	
	return float(r)

def clean_name(source_name):
	"""
		Nettoie le nom du jeu.
		
		Supprime les tags et si le jeu termine par ", The", le "The" est déplacé au début.
	"""
	
	try:
		game_clean_name = source_name[0:source_name.index('(')].strip()
	except ValueError:
		game_clean_name = source_name
	
	if game_clean_name.endswith(', The'):
		game_clean_name = 'The ' + game_clean_name[0:game_clean_name.index(', The')]
	
	return game_clean_name

class RCException(Exception):
	pass
