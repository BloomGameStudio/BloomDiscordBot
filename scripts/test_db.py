#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import SessionLocal, Event, OngoingVote, Config, Contributor
from sqlalchemy import text

def display_existing_data(session):
    """Display all existing data in the database"""
    print("\n=== Existing Data in Database ===")
    
    print("\nExisting Contributors:")
    contributors = session.query(Contributor).all()
    print(f"Total contributors: {len(contributors)}")
    for c in contributors:
        print(f"Server: {c.server_name}, UID: {c.uid}, Note: {c.note}, Emoji: {c.emoji_id}")
    
    print("\nExisting Events:")
    events = session.query(Event).all()
    print(f"Total events: {len(events)}")
    for e in events:
        print(f"Event ID: {e.event_id}, Guild ID: {e.guild_id}, Posted at: {e.posted_at}, Notified at: {e.notified_at}")
    
    print("\nExisting Ongoing Votes:")
    votes = session.query(OngoingVote).all()
    print(f"Total ongoing votes: {len(votes)}")
    for v in votes:
        print(f"Proposal ID: {v.proposal_id}, Title: {v.title}")

def cleanup_test_data(session):
    """Clean up any test data we've inserted"""
    print("\nCleaning up test data...")
    session.query(Event).filter(Event.guild_id == 67890).delete()
    session.query(OngoingVote).filter(OngoingVote.proposal_id.like('test_proposal_%')).delete()
    session.query(Contributor).filter(Contributor.uid.like('user_%')).delete()
    session.commit()
    print("Cleanup completed!")

def test_database():
    try:
        with SessionLocal() as session:
            # Display existing data first
            display_existing_data(session)
            
            # Clean up any existing test data first
            cleanup_test_data(session)
            
            # List all tables
            print("\nListing all tables:")
            result = session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            for table in result:
                print(f"- {table[0]}")
            
            # Test Event insertion
            print("\nTesting Event insertion:")
            event_id = random.randint(100000, 999999)
            new_event = Event(
                event_id=event_id,
                guild_id=67890,  # Using this as a marker for test data
                posted_at=datetime.now().timestamp()
            )
            session.add(new_event)
            session.commit()
            
            # Verify Event insertion
            print("Querying events:")
            events = session.query(Event).filter(Event.guild_id == 67890).all()
            for event in events:
                print(f"Event ID: {event.event_id}, Guild ID: {event.guild_id}, Posted at: {event.posted_at}")
            
            # Test OngoingVote insertion
            print("\nTesting OngoingVote insertion:")
            proposal_id = f"test_proposal_{random.randint(1000, 9999)}"
            new_vote = OngoingVote(
                proposal_id=proposal_id,
                draft={"title": "Test Proposal", "content": "Test Content"},
                end_time=datetime.now().timestamp(),
                title="Test Vote",
                channel_id="123",
                thread_id="456",
                message_id="789"
            )
            session.add(new_vote)
            session.commit()
            
            # Verify OngoingVote insertion
            print("Querying ongoing votes:")
            votes = session.query(OngoingVote).filter(OngoingVote.proposal_id.like('test_proposal_%')).all()
            for vote in votes:
                print(f"Proposal ID: {vote.proposal_id}, Title: {vote.title}")

            # Test Contributor insertion
            print("\nTesting Contributor insertion:")
            uid = f"user_{random.randint(100000, 999999)}"
            new_contributor = Contributor(
                uid=uid,
                note="Test Contributor",
                server_name="Bloom Studio",
                emoji_id="🌟"
            )
            session.add(new_contributor)
            session.commit()

            # Verify Contributor insertion
            print("Querying test contributors:")
            contributors = session.query(Contributor).filter(Contributor.uid.like('user_%')).all()
            for contributor in contributors:
                print(f"UID: {contributor.uid}, Server: {contributor.server_name}, Emoji: {contributor.emoji_id}, Note: {contributor.note}")
            
            print("\nTests completed successfully!")
            
            # Clean up after tests
            cleanup_test_data(session)
            
            return True
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_database()
    sys.exit(0 if success else 1) 