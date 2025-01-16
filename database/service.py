from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from .models import SessionLocal, Config, Contributor, Event, OngoingVote, Base, engine

@contextmanager
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DatabaseService:
    @staticmethod
    def init_db():
        """Initialize database tables"""
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def get_ongoing_votes() -> Dict[str, Any]:
        """Get all ongoing votes"""
        with get_db() as db:
            votes = db.query(OngoingVote).all()
            return {
                vote.proposal_id: {
                    "draft": vote.draft,
                    "end_time": vote.end_time,
                    "yes_count": vote.yes_count,
                    "title": vote.title,
                    "channel_id": vote.channel_id,
                    "thread_id": vote.thread_id,
                    "message_id": vote.message_id
                }
                for vote in votes
            }

    def get_ongoing_vote(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get an ongoing vote by proposal ID"""
        with SessionLocal() as session:
            vote = session.query(OngoingVote).filter_by(proposal_id=proposal_id).first()
            if not vote:
                return None
            return {
                "proposal_id": vote.proposal_id,
                "draft": vote.draft,
                "end_time": vote.end_time,
                "title": vote.title,
                "channel_id": vote.channel_id,
                "thread_id": vote.thread_id,
                "message_id": vote.message_id
            }

    def save_ongoing_vote(self, vote_data: Dict[str, Any]) -> None:
        """Save an ongoing vote to the database"""
        with SessionLocal() as session:
            vote = OngoingVote(
                proposal_id=vote_data["proposal_id"],
                draft=vote_data["draft"],
                end_time=vote_data["end_time"],
                title=vote_data["title"],
                channel_id=vote_data["channel_id"],
                thread_id=vote_data["thread_id"],
                message_id=vote_data["message_id"]
            )
            session.add(vote)
            session.commit()

    @staticmethod
    def get_posted_events() -> List[int]:
        """Get all posted event IDs"""
        with get_db() as db:
            events = db.query(Event.event_id).filter(
                Event.posted_at.isnot(None)
            ).all()
            return [event.event_id for event in events]

    @staticmethod
    def save_posted_event(event_id: int, guild_id: int):
        """Save a posted event"""
        with get_db() as db:
            event = Event(
                event_id=event_id,
                guild_id=guild_id,
                posted_at=datetime.now().timestamp()
            )
            db.add(event)
            db.commit()

    @staticmethod
    def get_notified_events() -> Dict[int, float]:
        """Get all notified events"""
        with get_db() as db:
            events = db.query(Event).filter(
                Event.notified_at.isnot(None)
            ).all()
            return {
                event.event_id: event.notified_at
                for event in events
            }

    @staticmethod
    def save_notified_event(event_id: int, guild_id: int, notified_at: float):
        """Save a notified event"""
        with get_db() as db:
            event = db.query(Event).filter_by(event_id=event_id).first()
            if event:
                event.notified_at = notified_at
            else:
                event = Event(
                    event_id=event_id,
                    guild_id=guild_id,
                    notified_at=notified_at
                )
                db.add(event)
            db.commit()

    @staticmethod
    def get_contributors_and_emoji_dicts():
        """Get contributors and emoji dictionaries"""
        with get_db() as db:
            contributors = db.query(Contributor).all()
            
            result = {
                "Bloom Studio": [],
                "Bloom Collective": []
            }
            emoji_dicts = {
                "Bloom Studio": {},
                "Bloom Collective": {}
            }
            
            for c in contributors:
                result[c.server_name].append({
                    "uid": c.uid,
                    "note": c.note
                })
                if c.emoji_id:
                    emoji_dicts[c.server_name][c.emoji_id] = c.uid
                
            return result, emoji_dicts