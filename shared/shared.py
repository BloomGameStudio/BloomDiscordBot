import configparser
# Load configuration
config = configparser.ConfigParser()
config.read('config/config.ini')  

current_governance_id = config.getint('ID_START_VALUES', 'governance_id')
current_budget_id = config.getint('ID_START_VALUES', 'budget_id')

