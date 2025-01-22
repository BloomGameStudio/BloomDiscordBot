#!/usr/bin/env python3
from database.service import DatabaseService

if __name__ == "__main__":
    try:
        DatabaseService.init_db()
        exit(0)
    except Exception as e:
        print(f"Error initializing database: {e}")
        exit(1)
