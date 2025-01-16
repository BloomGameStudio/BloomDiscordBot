#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Base
from database.service import DatabaseService

def init_database():
    try:
        # Get database URL from environment or use default
        database_url = os.getenv("DATABASE_URL", "postgresql://bloom:bloom@localhost:5432/bloombot")
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        print(f"Connecting to database at {database_url}...")
        engine = create_engine(database_url)
        
        print("Creating database tables...")
        Base.metadata.create_all(engine)
        
        print("Database tables created successfully!")
        return True
        
    except SQLAlchemyError as e:
        print(f"Database error occurred: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)