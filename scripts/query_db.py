#!/usr/bin/env python3
import os
import argparse
import sys
from datetime import datetime
from database.models import SessionLocal, Contributor, Event, OngoingVote, ConcludedVote
from logger.logger import logger
from database.service import DatabaseService


def format_timestamp(ts):
    """Convert timestamp to readable datetime"""
    if ts:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    return "None"


def query_contributors(session, server_id=None):
    """Query and display contributors"""
    db_service = DatabaseService(session=session)

    if server_id is None:
        logger.info("Querying all contributors")
    elif server_id <= 0:
        logger.warning(f"Invalid server_id: {server_id}. Must be a positive integer.")
        return None

    print("\n=== Contributors ===")
    contributors = (
        db_service.get_contributors_from_db(server_id)
        if server_id
        else db_service.get_all_contributors()
    )

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


def query_events(session):
    """Query and display events"""
    db_service = DatabaseService(session=session)
    print("\n=== Events ===")

    events = db_service.get_all_events()
    if events:
        logger.info("Found %d events", len(events))
        for e in events:
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
    db_service = DatabaseService(session=session)
    print("\n=== Ongoing Votes ===")

    votes = db_service.get_ongoing_votes()
    if votes:
        logger.info("Found %d ongoing votes", len(votes))
        for proposal_id, v in votes.items():
            print(f"Proposal ID: {proposal_id}")
            print(f"Title: {v['title']}")
            print(f"End Time: {format_timestamp(v['end_time'])}")
            print("-" * 40)
    else:
        logger.info("No ongoing votes found")
        print("No ongoing votes found")


def query_concluded_votes(session, passed_only=False):
    """Query and display concluded votes"""
    logger.info("Querying concluded votes%s", " (passed only)" if passed_only else "")
    print("\n=== Concluded Votes ===")

    db_service = DatabaseService(session=session)
    concluded_votes = db_service.get_concluded_votes(passed_only=passed_only)

    if concluded_votes:
        logger.info("Found %d concluded votes", len(concluded_votes))
        for proposal_id, v in concluded_votes.items():
            print(f"Proposal ID: {proposal_id}")
            print(f"Title: {v['title']}")
            print(f"Yes Count: {v['yes_count']}")
            print(f"No Count: {v['no_count']}")
            print(f"Abstain Count: {v['abstain_count']}")
            print(f"Passed: {v['passed']}")
            print(f"Concluded at: {format_timestamp(v['concluded_at'])}")
            print(f"Snapshot URL: {v.get('snapshot_url', 'N/A')}")
            print("-" * 40)
    else:
        logger.info("No concluded votes found")
        print("No concluded votes found")


def main():
    parser = argparse.ArgumentParser(description="Query the database")
    parser.add_argument(
        "--table",
        choices=["all", "contributors", "events", "ongoing_votes", "concluded_votes"],
        required=True,
        help="Table to query",
    )
    parser.add_argument(
        "--server_id",
        type=int,
        help="Server ID to filter contributors (optional)",
    )
    parser.add_argument(
        "--passed_only",
        action="store_true",
        help="Show only passed votes (for concluded_votes)",
    )

    args = parser.parse_args()

    with SessionLocal() as session:
        if args.table == "all":
            query_contributors(session)
            query_events(session)
            query_ongoing_votes(session)
            query_concluded_votes(session)
        elif args.table == "contributors":
            query_contributors(session, args.server_id)
        elif args.table == "events":
            query_events(session)
        elif args.table == "ongoing_votes":
            query_ongoing_votes(session)
        elif args.table == "concluded_votes":
            query_concluded_votes(session, args.passed_only)


if __name__ == "__main__":
    main()
