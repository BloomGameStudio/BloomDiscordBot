from tinydb import TinyDB, Query

# Initialize the TinyDB database
db = TinyDB('data/db.json')

# Function to insert data into the database
def insert_data(table_name, data):
    table = db.table(table_name)
    table.insert(data)

# Function to update data in the database
def update_data(table_name, key, value, new_data):
    table = db.table(table_name)
    table.update(new_data, key == value)

# Function to delete data from the database
def delete_data(table_name, key, value):
    table = db.table(table_name)
    table.remove(key == value)

# Function to query data from the database
def query_data(table_name, key, value):
    table = db.table(table_name)
    return table.search(key == value)