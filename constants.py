import configparser
import os

# Read config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Access values in the config file
GUILD_ID = int(config['DISCORD']['GUILD_ID'])
GENERAL_CHANNEL_ID = int(config['DISCORD']['GENERAL_CHANNEL_ID'])
FILE_PATH = config['DISCORD']['FILE_PATH']
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')