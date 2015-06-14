ROMC
====

A little Python script to clean a set of games (roms or Mame). The games are filtered based on there name.

If the files name are well taged, is it possible to filter games by country, dump version, dump quality, set, etc.

After filtering and cleaning operations, romc create an XML file compatible with HyperSpin Front-End, used as database.

Author
------

This script is made and maintained by __bsymon__ for HyperSpin community.

When to use it ?
----------------

Use this script when you have a set of games to clean. The filename of the games have to look like this :

- Astro Boy - Omega Factor (E) (M6)
- Bomberman Max 2 - Red (U) [hIR00]
- Ironsword - Wizards & Warriors II (E) [!]
- Airwolf (U) [b5]
- Castlevania (U) (V1.0) [t2]
- Ironman - X-O Manowar in Heavy Metal (U) [S][!]
- ...

The things at the end of the game name are called flags, and romc looks at them to do its job. The flags give information about the dump of the game.

romc also works with Mame set (see [Mame specifics](#mame-specifics)).

Configuration
-------------

Create a file called `config.ini`. In this file will live the base configuration for romc and the configuration for each system you want to clean.

	[BaseConfig]
	; Display log during the operations. (true or false)
	log_process = true
	
	; The quantity of information displayed in the log. (an integer between 1 and 3)
	log_level = 1
	
	; The filepath where to store the complete log.
	log_file = ''
	
	; The suffix to add to the string that exceed the max length of --strl.
	csv_long_string_suffix=...
	
	
	; Per system config. Create one section per system.
	[%System%]
	; The path to the directory containing all your roms
	dir = ''
	
	; A comma-separated list of file extentions. If empty, all the files in "dir" will be cleaned. If not empty, only the files of that extentions will be cleaned. 
	ext = ''
	
	; A comma-separated list of the countries you want to select, classed by importance.
	country = ''
	
	; A comma-separated list of the countries you don't want.
	exclude_country = 
	
	; If the country of the game cannot be found, whether select it of reject it. (true or false)
	allow_no_country = true
	
	; Select only legit games (no hack, prototype or bootleg). (true or false)
	only_legit = true
	
	; Select special games.
	special = true
	
	; A list of flags to be considered as valid.
	flags = ''
	
	; Look for additionals data online. (true or false)
	online_data = false
	
	; A comma-separated list of countries. If empty, will search data for all the games. If not empty, only the games that have their country listed will be searched.
	online_data_lang = ''
	
	; Which API use for online data. (whether "jvc", "ign", or "mobygames")
	online_api = ''
	
	; Set to true romc will download the game cover (only available with JVC API).
	download_covers = true
	
	; Indicate if the system should be considered as Mame. (true or false)
	is_mame = false
	
	; If the system is Mame, the path to the DAT file.
	dat_file = ''
	
	; A comma-separated list of filepath. Usualy INI files, listing all the games supported by Mame, by genre.
	cat_files = ''
	
	; A comma-separated list of genre to exclude. If empty, all the games will be selected. If not empty, the games that have their genre listed here will be ignored.
	ignore_cat = ''
	
	; Same as "ignore_cat", but the games will be moved in a directory called "_moved" ("move_files" have to be true).
	exclude_cat = ''
	
	; Wheter moves files or not. (true or false)
	move_files = false

How does it work ?
------------------

There is two stages. __First one__, romc scan all your games in `dir`, and then :

For Mame

1. Ignore the game if the genre is in `ignore_cat` or `exclude_cat`.
2. Ignore the game if the set number is not 1.
3. Ignore the game if it is a hack, bootleg or a protoype, and `only_legit` is `true`.
4. Ignore the game if the country cannot be found, and `allow_no_coutry` is `false`.
5. Ignore the game if the country is in `exclude_country`.

For the others systems

1. Ignore the game if it is special and `special` is `false`.
2. Ignore the game if it is a hack and `only_legit` is `true`.
3. Ignore the game if the dump is not good _(flag [!], or the higher fixe [fX])_.
4. Ignore the game if the country cannot be found, and `allow_no_coutry` is `false`.
5. Ignore the game if the country is in `exclude_country`. 

The name of the game is then cleaned, to remove all the tags and only keep the name. Is it possible that a game exists in several version (dump quality, version, country, etc.)

__So here the second stage__ : romc will calculate a score for each version of a game, depending on the country and the dump version. The country is chosen by order of preference, according to `country` config option.

Example : your `country` look like this `Europe,USA,Japan`. So your prefered country is Europe, then USA and finaly Japan.

For the dump version the higher is the better.

After all this process, only one game is selected.

Online data
-----------

romc can search additionals informations for the games. To do so, romc proposes 3 API :

- __jvc__ : get the data on [Jeuxvideo.com](http://www.jeuxvideo.com) (french website)
- __ign__ : get the data on [IGN.com](http://www.ign.com)
- __mobygames__ : get the data on [Mobygames.com](http://www.mobygames.com) (only works for Mame)

For better results, _jvc_ and _ign_ API first perform a Google search with this syntaxe : `site:(adress) (game name) (system)`

Example : `site:www.jeuxvideo.com Crash Bandicoot Playstation`

__(game)__ is the name of the game after cleaning, and __(system)__ is the name of the system, as write in your config.ini.

#### Notes

romc have to perform at least one request per game. That could do __a lot__ of requests. For example, a Mame set of games can contains up to __+10 000 games__ ! romc will take care to filter these games, but according to your config, you can still have thousands of games.

This means thousands of request.

To reduce the risk of "DDoS" or server ban (Google can do that), between each request an interval of 2 secondes has been set. So if you have a lot of games, get data for all of them can take several minutes, or hours. Be patient !

#### Covers

You can download the covers of your games with romc. Set configuration option `download_covers` to true for your system. The files will be downloaded in "covers/" folder.

_This option is only available for JVC API ([Jeuxvideo.com](http://www.jeuxvideo.com))._

Countries
---------

For a better filtering, you can tell romc which countries you prefer to select (`country`) in your set of games, or which ones to exclude (`exclude_country`). It's a white-list and a black-list.

The `allow_no_country` config option can acts like a gray-list. If romc cannot find the country of a game, `allow_no_country` set to `true` allows the game to be selected. If set to `false`, the game will be ignored.

Here is a list of Mame countries I've identified :

- Japan
- J (for Japan)
- USA
- US
- Europe
- E (for Europe)
- World

This list is not complete. If you have identified others countries, let me know. To do so, create a new __issue__ with the flag __country__. I will add them here for a better documentation.

And a list of countries for others systems (like SNES, GBA, PS1, etc.) :

- 1 (Japan & Korea)
- 4 (USA & Brazil NTSC)
- A (Australia)
- B (non USA, on Genesis)
- C (China)
- E (Europe)
- F (France)
- F (World, on Genesis)
- FC (French Canadian)
- FN (Finland)
- G (Germany)
- GR (Greece)
- HK (Hong Kong)
- H (Holland)
- J (Japan)
- K (Korea)
- NL (Netherlands)
- PD (Public Domain)
- S (Spain)
- SW (Sweden)
- U (USA)
- UK (England)
- Unk (Unknow Country)
- I (Italy)
- Unl (Unlicensed)
- UE (???)

_Source [VNotes Chronicle](http://www.vnoteschronicle.com/notes/rom-codes-explained)_

Mame specifics
--------------

To tell romc that a system have to be considered as Mame, set `is_mame` to `true`. A this point, you have to provide the path to you Mame DAT file (in `dat_file`). This is the only way to get data for the games.

To get Mame DAT, go to `mame.exe` directory and launch a new command line. Then type : `mame.exe -listxml > mame.dat`

With Mame, is it also possible to filter your game by genre. First you must have one or plus catlist files. You can download them here : [EMMA](http://www.progettoemma.net/?catlist)

Then, in `cat_files` config option, you set one or plus path to the catlist files (comma-separated).

After this, in `ignore_cat` or `exclude_cat`, you indicate which genre you want to ignore or exclude.

#### Notes

`ignore_cat` only ignore the game. It is not added in the final XML.
`exclude_cat` acts like `ignore_cat`, but the game will also be moved in a separeted directory, called "_moved".

Is it important to note that games, to works with Mame, have often need of dependancies. If you place all the genre you don't want in `exclude_cat`, you can break some games !

Use `ignore_cat` for the BIOS "game", so your are sure to do not break your games, and `exclude_cat` for Mahjong or Adult games, for example.

Usage
-----

First you need Python 2.7 : [Download Python](https://www.python.org/downloads/)

Then go in romc directory, launch a new command line and type : `python romc.py (system) [-p] [-c] [--csv [FIELD, ...]]` where `(system)` is one of the systems listed in `config.ini`.

#### Options

- `-p` : Also generate HyperPause game info INI file, located at __HyperPause__.
- `-c` : Use an already generated _system_.xml file.
- `--csv` : Generate a CSV file _system_.csv. You can specify what fields you want.
- `--strl` : Determine the maximum length of strings in the CSV file.

##### CSV fields

- __game__ : The name of the game.
- __original_name__ : The original name of the game (the filename).
- __country__ : The country.
- __version__ : The dump version of the game.
- __editor__ : Editor, manufacturer, developper, ...
- __year__ : Release year.
- __genre__ : Genre.
- __resume__ : A description of the game.
- __note__ : The game note.
- __rating__ : The PEGI or ESRB rating.
- __score__ : The score the game had during the second stage. If you use `-c` option, will be equal to 0.
- __onlineData__ : Whether the game has online data or not.

__Example__ : `python romc.py Mame -c --csv game year country note`

#### Dependencies

romc uses :

- __[lxml](http://lxml.de/)__
- __[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/bs4/doc/)__
- __[google](https://breakingcode.wordpress.com/2010/06/29/google-search-python/)__ _not an official Google API_

You have to install them in order to get romc to work. Use `pip` for that.

Bugs and improvements
---------------------

If you find bugs or if you any ideas to improve romc, please create a new __issue__ on GitHub ! Don't hesitate to fork !!

#### Bugs

- There is a "bug" in RCRomParser.py, with the regex. With name like this `Advance Wars 2 - Black Hole Rising (U) (Balance (V10) Hack)`, the word "Hack" is not found, but "V10" is. This cause the game to be considered as legit, with a dump version of 10.
