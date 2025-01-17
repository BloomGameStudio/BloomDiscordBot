#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import SessionLocal, Contributor, Event, OngoingVote


def load_json_file(file_path):
    """Load a JSON file if it exists, return empty dict if it doesn't"""
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Warning: Could not load {file_path}: {e}")
        return {}


def migrate_contributors(session, data):
    """Migrate contributors from JSON to database"""
    try:
        print("\n=== Migrating Contributors ===")
        if not data:
            print("No contributors data to migrate.")
            return 0

        # Clear existing contributors
        session.query(Contributor).delete()
        session.commit()

        total_migrated = 0
        for server_name, server_data in data["servers"].items():
            contributors = server_data["contributors"]
            emoji_dict = server_data["emoji_dictionary"]

            print(f"\nMigrating contributors for {server_name}...")
            for contributor in contributors:
                # Find the emoji ID for this contributor
                emoji_id = None
                for emoji, uid in emoji_dict.items():
                    if uid == contributor["uid"]:
                        emoji_id = emoji
                        break

                new_contributor = Contributor(
                    uid=contributor["uid"],
                    note=contributor["note"],
                    server_name=server_name,
                    emoji_id=emoji_id,
                )
                session.add(new_contributor)
                total_migrated += 1

        session.commit()
        print(f"Successfully migrated {total_migrated} contributors")
        return total_migrated
    except Exception as e:
        print(f"Error migrating contributors: {e}")
        session.rollback()
        return 0


def migrate_events(session, posted_events, notified_events):
    """Migrate events from JSON to database"""
    try:
        print("\n=== Migrating Events ===")
        # Clear existing events
        session.query(Event).delete()
        session.commit()

        total_migrated = 0

        # Handle posted events
        if posted_events:
            print("\nMigrating posted events...")
            for event_id in posted_events:
                new_event = Event(
                    event_id=int(event_id),
                    posted_at=datetime.now().timestamp(),  # Use current time as we don't have original timestamp
                )
                session.add(new_event)
                total_migrated += 1

        # Handle notified events
        if notified_events:
            print("\nMigrating notified events...")
            for event_id, notified_at in notified_events.items():
                # Update existing event or create new one
                event = session.query(Event).filter_by(event_id=int(event_id)).first()
                if event:
                    event.notified_at = notified_at
                else:
                    new_event = Event(event_id=int(event_id), notified_at=notified_at)
                    session.add(new_event)
                    total_migrated += 1

        session.commit()
        print(f"Successfully migrated {total_migrated} events")
        return total_migrated
    except Exception as e:
        print(f"Error migrating events: {e}")
        session.rollback()
        return 0


def migrate_ongoing_votes(session, data):
    """Migrate ongoing votes from JSON to database"""
    try:
        print("\n=== Migrating Ongoing Votes ===")
        if not data:
            print("No ongoing votes to migrate.")
            return 0

        # Clear existing votes
        session.query(OngoingVote).delete()
        session.commit()

        total_migrated = 0
        for proposal_id, vote_data in data.items():
            new_vote = OngoingVote(
                proposal_id=proposal_id,
                draft=vote_data.get("draft", {}),
                end_time=vote_data.get("end_time", 0),
                yes_count=vote_data.get("yes_count", 0),
                title=vote_data.get("title", ""),
                channel_id=vote_data.get("channel_id", ""),
                thread_id=vote_data.get("thread_id", ""),
                message_id=vote_data.get("message_id", ""),
            )
            session.add(new_vote)
            total_migrated += 1

        session.commit()
        print(f"Successfully migrated {total_migrated} ongoing votes")
        return total_migrated
    except Exception as e:
        print(f"Error migrating ongoing votes: {e}")
        session.rollback()
        return 0


def verify_migration(session):
    """Verify the migrated data"""
    print("\n=== Verifying Migration ===")

    contributors = session.query(Contributor).all()
    print(f"\nContributors in database: {len(contributors)}")
    for c in contributors:
        print(
            f"Server: {c.server_name}, UID: {c.uid}, Note: {c.note}, Emoji: {c.emoji_id}"
        )

    events = session.query(Event).all()
    print(f"\nEvents in database: {len(events)}")
    for e in events:
        print(
            f"Event ID: {e.event_id}, Posted at: {e.posted_at}, Notified at: {e.notified_at}"
        )

    votes = session.query(OngoingVote).all()
    print(f"\nOngoing votes in database: {len(votes)}")
    for v in votes:
        print(
            f"Proposal ID: {v.proposal_id}, Title: {v.title}, Yes Count: {v.yes_count}"
        )


def main():
    try:
        # Load all JSON files
        contributors_data = load_json_file("data/contributors.json")
        posted_events_data = load_json_file("data/posted_events.json")
        notified_events_data = load_json_file("data/notified_events.json")
        ongoing_votes_data = load_json_file("data/ongoing_votes.json")

        with SessionLocal() as session:
            # Perform migrations
            migrate_contributors(session, contributors_data)
            migrate_events(session, posted_events_data, notified_events_data)
            migrate_ongoing_votes(session, ongoing_votes_data)

            # Verify the migration
            verify_migration(session)

            print("\nMigration completed successfully!")
            return True

    except Exception as e:
        print(f"An error occurred during migration: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
