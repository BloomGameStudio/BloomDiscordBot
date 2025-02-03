#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
from database.models import SessionLocal
from database.service import DatabaseService
from logger.logger import logger
import time


def load_json_file(file_path):
    """Load a JSON file if it exists, return empty dict if it doesn't"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Warning: Could not load {file_path}: {e}")
        return {}


def migrate_data():
    """Main migration function"""
    try:
        session = SessionLocal()
        db_service = DatabaseService(session=session)

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

        contributors_data = load_json_file(os.path.join(data_dir, "contributors.json"))
        events_data = load_json_file(os.path.join(data_dir, "events.json"))
        ongoing_votes_data = load_json_file(
            os.path.join(data_dir, "ongoing_votes.json")
        )
        notified_events_data = load_json_file(
            os.path.join(data_dir, "notified_events.json")
        )
        posted_events_data = load_json_file(
            os.path.join(data_dir, "posted_events.json")
        )

        for event_id in posted_events_data:
            if str(event_id) in events_data:
                events_data[str(event_id)]["posted_at"] = int(time.time())

        for event_id, notified_time in notified_events_data.items():
            if str(event_id) in events_data:
                events_data[str(event_id)]["notified_at"] = int(notified_time)

        db_service.migrate_contributors(contributors_data)
        db_service.migrate_events(events_data)
        db_service.migrate_ongoing_votes(ongoing_votes_data)

        logger.info("Migration completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False
    finally:
        session.close()


if __name__ == "__main__":
    success = migrate_data()
    sys.exit(0 if success else 1)
