#!/usr/bin/env python3
import os
import sys
import json
from datetime import datetime
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
        if not data or "servers" not in data:
            print("No contributors data to migrate.")
            return 0

        session.query(Contributor).delete()
        session.commit()

        total_migrated = 0
        for server_name, server_data in data["servers"].items():
            contributors = server_data.get("contributors", [])
            emoji_dict = server_data.get("emoji_dictionary", {})

            print(f"\nMigrating contributors for {server_name}...")
            for contributor in contributors:
                emoji_id = None
                for emoji, uid in emoji_dict.items():
                    if uid == contributor["uid"]:
                        emoji_id = emoji
                        break

                new_contributor = Contributor(
                    uid=contributor["uid"],
                    note=contributor.get("note", ""),
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


def migrate_events(session, data):
    """Migrate events from JSON to database"""
    try:
        print("\n=== Migrating Events ===")
        if not data:
            print("No events data to migrate.")
            return 0

        session.query(Event).delete()
        session.commit()

        total_migrated = 0
        for event_id, event_data in data.items():
            new_event = Event(
                event_id=int(event_id),
                guild_id=event_data.get("guild_id", 0),
                posted_at=event_data.get("posted_at", 0),
                notified_at=event_data.get("notified_at", 0),
            )
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

        session.query(OngoingVote).delete()
        session.commit()

        total_migrated = 0
        for proposal_id, vote_data in data.items():
            new_vote = OngoingVote(
                proposal_id=proposal_id,
                draft=vote_data.get("draft", {}),
                end_time=vote_data.get("end_time", 0),
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
        print(f"Event ID: {e.event_id}, Guild ID: {e.guild_id}")

    votes = session.query(OngoingVote).all()
    print(f"\nOngoing votes in database: {len(votes)}")
    for v in votes:
        print(f"Proposal ID: {v.proposal_id}, Title: {v.title}")


def migrate_data():
    """Main migration function"""
    try:
        session = SessionLocal()

        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

        contributors_data = load_json_file(os.path.join(data_dir, "contributors.json"))
        events_data = load_json_file(os.path.join(data_dir, "events.json"))
        ongoing_votes_data = load_json_file(
            os.path.join(data_dir, "ongoing_votes.json")
        )

        migrate_contributors(session, contributors_data)
        migrate_events(session, events_data)
        migrate_ongoing_votes(session, ongoing_votes_data)

        verify_migration(session)

        session.close()
        return True

    except Exception as e:
        print(f"Error during migration: {e}")
        return False


if __name__ == "__main__":
    if not os.getenv("DB_PASSWORD"):
        print("Warning: DB_PASSWORD not set. Using default configuration.")

    success = migrate_data()
    sys.exit(0 if success else 1)
