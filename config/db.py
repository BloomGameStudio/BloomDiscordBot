from tinydb import TinyDB
from logger.logger import logger

# Initialize the TinyDB database
db = TinyDB('data/db.json')

# Function to query data from the database
def query_data(table_name, server_name):
    logger.info(f"Querying data from table {table_name} for server {server_name}")
    table = db.table(table_name)
    server_data = table.get(doc_id=server_name)
    if server_data:
        return server_data
    else:
        return None