from tinydb import TinyDB, Query

# Initialize the database
db = TinyDB('data/db.json')

def get_contributors_table():
    return db.table('contributors')

def get_ongoing_votes_table():
    return db.table('ongoing_votes')

def get_posted_events_table():
    return db.table('posted_events')