import pytest
import os
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from database.models import Base

def get_alembic_config(url):
    """Create Alembic config for testing"""
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", "database/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    return alembic_cfg

@pytest.fixture(scope="function")
def test_db():
    """Create a test database for migration testing"""
    url = "sqlite:///:memory:"
    engine = create_engine(url)
    
    # Create initial schema
    Base.metadata.create_all(engine)
    
    # Add yes_count column manually since SQLite doesn't support DROP COLUMN
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE temp_ongoing_votes (
                id INTEGER PRIMARY KEY,
                proposal_id VARCHAR,
                draft JSON,
                end_time FLOAT,
                title VARCHAR,
                channel_id VARCHAR,
                thread_id VARCHAR,
                message_id VARCHAR,
                yes_count INTEGER
            )
        """))
        conn.commit()
    
    return engine, url

def test_table_exists(test_db):
    """Test that tables exist after initial creation"""
    engine, _ = test_db
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "ongoing_votes" in tables
    assert "events" in tables
    assert "contributors" in tables

def test_columns_exist(test_db):
    """Test that expected columns exist in tables"""
    engine, _ = test_db
    inspector = inspect(engine)
    
    ongoing_votes_columns = {col['name'] for col in inspector.get_columns('ongoing_votes')}
    assert 'proposal_id' in ongoing_votes_columns
    assert 'draft' in ongoing_votes_columns
    assert 'end_time' in ongoing_votes_columns
    
    events_columns = {col['name'] for col in inspector.get_columns('events')}
    assert 'event_id' in events_columns
    assert 'guild_id' in events_columns
    assert 'posted_at' in events_columns
    
    contributors_columns = {col['name'] for col in inspector.get_columns('contributors')}
    assert 'uid' in contributors_columns
    assert 'note' in contributors_columns
    assert 'server_name' in contributors_columns 