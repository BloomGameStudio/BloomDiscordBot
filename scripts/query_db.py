#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime

# Set up database connection environment variables BEFORE importing models
os.environ["DB_USER"] = "bloom"
os.environ["DB_PASSWORD"] = "bloom"
os.environ["DB_HOST"] = "localhost"
os.environ["DB_PORT"] = "5432"
os.environ["DB_NAME"] = "bloombot"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import SessionLocal, Contributor, Event, OngoingVote, ConcludedVote
from logger.logger import logger


def format_timestamp(ts):
    """Convert timestamp to readable datetime"""
    if ts:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return "None"


def query_contributors(session, server_id=None):
    """Query and display contributors"""
    logger.info("Querying contributors%s", f" for server {server_id}" if server_id else "")
    print("\n=== Contributors ===")
    query = session.query(Contributor)
    if server_id:
        query = query.filter(Contributor.server_name == str(server_id))
    contributors = query.all()

    if contributors:
        logger.info("Found %d contributors", len(contributors))
        for c in contributors:
            print(f"ID: {c.id}")
            print(f"UID: {c.uid}")
            print(f"Note: {c.note}")
            print(f"Server: {c.server_name}")
            print(f"Emoji: {c.emoji_id}")
            print("-" * 40)
    else:
        logger.info("No contributors found")
        print("No contributors found")


def query_events(session, guild_id=None):
    """Query and display events"""
    logger.info("Querying events%s", f" for guild {guild_id}" if guild_id else "")
    print("\n=== Events ===")
    query = session.query(Event)
    if guild_id:
        query = query.filter(Event.guild_id == guild_id)
    events = query.all()

    if events:
        logger.info("Found %d events", len(events))
        for e in events:
            print(f"ID: {e.id}")
            print(f"Event ID: {e.event_id}")
            print(f"Guild ID: {e.guild_id}")
            print(f"Posted at: {format_timestamp(e.posted_at)}")
            print(f"Notified at: {format_timestamp(e.notified_at)}")
            print("-" * 40)
    else:
        logger.info("No events found")
        print("No events found")


def query_ongoing_votes(session):
    """Query and display ongoing votes"""
    logger.info("Querying ongoing votes")
    print("\n=== Ongoing Votes ===")
    ongoing_votes = session.query(OngoingVote).all()

    if ongoing_votes:
        logger.info("Found %d ongoing votes", len(ongoing_votes))
        for v in ongoing_votes:
            print(f"ID: {v.id}")
            print(f"Proposal ID: {v.proposal_id}")
            print(f"Title: {v.title}")
            print(f"End Time: {format_timestamp(v.end_time)}")
            print(f"Channel ID: {v.channel_id}")
            print(f"Thread ID: {v.thread_id}")
            print("-" * 40)
    else:
        logger.info("No ongoing votes found")
        print("No ongoing votes found")


def query_concluded_votes(session, passed_only=False):
    """Query and display concluded votes"""
    logger.info("Querying concluded votes%s", " (passed only)" if passed_only else "")
    print("\n=== Concluded Votes ===")
    query = session.query(ConcludedVote)
    if passed_only:
        query = query.filter(ConcludedVote.passed == True)
    concluded_votes = query.order_by(ConcludedVote.concluded_at.desc()).all()

    if concluded_votes:
        logger.info("Found %d concluded votes", len(concluded_votes))
        for v in concluded_votes:
            print(f"ID: {v.id}")
            print(f"Proposal ID: {v.proposal_id}")
            print(f"Title: {v.title}")
            print(f"Yes Count: {v.yes_count}")
            print(f"No Count: {v.no_count}")
            print(f"Abstain Count: {v.abstain_count}")
            print(f"Passed: {v.passed}")
            print(f"Concluded at: {format_timestamp(v.concluded_at)}")
            print(f"Snapshot URL: {v.snapshot_url}")
            print("-" * 40)
    else:
        logger.info("No concluded votes found")
        print("No concluded votes found")


def main():
    parser = argparse.ArgumentParser(description="Query the BloomBot database")
    parser.add_argument(
        "--table",
        choices=["contributors", "events", "ongoing_votes", "concluded_votes", "all"],
        help="Which table to query",
        required=True,
    )
    parser.add_argument(
        "--server-id", type=str, help="Filter contributors by server ID"
    )
    parser.add_argument("--guild-id", type=int, help="Filter events by guild ID")
    parser.add_argument(
        "--passed-only",
        action="store_true",
        help="Show only passed proposals for concluded votes",
    )

    args = parser.parse_args()
    logger.info("Starting database query with args: %s", vars(args))

    try:
        with SessionLocal() as session:
            if args.table == "contributors" or args.table == "all":
                query_contributors(session, args.server_id)

            if args.table == "events" or args.table == "all":
                query_events(session, args.guild_id)

            if args.table == "ongoing_votes" or args.table == "all":
                query_ongoing_votes(session)

            if args.table == "concluded_votes" or args.table == "all":
                query_concluded_votes(session, args.passed_only)

        logger.info("Database query completed successfully")
    except Exception as e:
        logger.error("Error querying database: %s", str(e))
        print(f"Error querying database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
