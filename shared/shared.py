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