# -*- coding: UTF-8 -*-

#-----------------------------#
#     MODEL PARSING KEYS      #
#-----------------------------#

#Pokemon
POKEMON_NAME_KEY = 'name'
POKEMON_URL_KEY = 'url'
POKEMON_ENS_ID_KEY = 'ens_id'
POKEMON_GENERATION_KEY = 'generation'

PRICE_CHANGE_NOMINAL_KEY = 'price_change_24h'
PRICE_CHANGE_PERCENT_KEY = 'price_change_percentage_24h'




#-----------------------------#
#         COLLECTIONS         #
#-----------------------------#
ENS_COLLECTION = '0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85'
NIGHTBIRDS_COLLECTION = '0x64b6b4142d4d78e49d53430c1d3939f2317f9085'
WASSIES_COLLECTION = '0x1D20A51F088492A0f1C57f047A9e30c9aB5C07Ea'
MOONBIRDS_COLLECTION = '0x23581767a106ae21c074b2276D25e5C3e136a68b'

#-----------------------------#
#          CONTRACTS          #
#-----------------------------#

#-----------------------------#
#    HUMAN READABLE ERRORS    #
#-----------------------------#
HR_ERROR_JSON_DECODE = 'Decoding JSON has failed'

#-----------------------------#
#          SPECIFICS          #
#-----------------------------#
POKEMON_GENERATIONS = 8

RULES_MESSAGE_ID = 1199535053194154044

DISCORD_ROLE_TRIGGERS = [
	{'name':'Client','emoji_id':1176399164154851368,'role':'Client Pod'},
	{'name':'Graphics & Design','emoji_id':980752213347549234,'role':'Graphics Pod'},
	{'name':'Backend','emoji_id':846911453839228938,'role':'Backend Pod'},
	{'name':'Gameplay & Story Pod','emoji_id':961338498525306980,'role':'Gameplay & Story Pod'},
	{'name':'Operations','emoji_id':945177584768004127,'role':'Policy & Ops Pod'},
	{'name':'Financial','emoji_id':887872297082449970,'role':'Donator'},
]

ROLE_WHEN_NEW_USER_CONFIRMED='contributors'

#-----------------------------#
#THESE ARE BOT/GUILD SPECIFIC #
#-----------------------------#
COLOR_CHANGING_ROLE = 'bloom-visual'
COMMAND_TRIGGERS = ['!']
PRICE_TRIGGERS = ['$']
GUILD_TRIGGER = 'Bloom Studio'