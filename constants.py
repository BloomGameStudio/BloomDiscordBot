import os

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GOVERNANCE_CHANNEL_ID = 1181503487440334938
GOVERNANCE_TALK_CHANNEL_ID = 1176395644261367828
GOVERNANCE_BUDGET_CHANNEL_ID = 1179949022287495198
new_proposal_emoji = "💡"


#This probably doesn't belong here.
import configparser
import logging
# Load configuration
config = configparser.ConfigParser()
config.read('config/config.ini')  

current_governance_id = config.getint('ID_START_VALUES', 'governance_id')
current_budget_id = config.getint('ID_START_VALUES', 'budget_id')

# Set up logging
logging_level = config.get('Logging', 'level', fallback='INFO')
numeric_logging_level = getattr(logging, logging_level.upper(), logging.INFO)
logging.basicConfig(level=numeric_logging_level)