from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from .models import SessionLocal, Config, Contributor, Event, OngoingVote, Base, engine


@contextmanager
def get_db() -> Generator:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseService:
    def __init__(self, session=None):
        """Initialize with optional session for testing"""
        self._session = session

    def _get_session(self):
        """Get database session - uses provided test session or creates new one"""
        if self._session is not None:
            return self._session
        return SessionLocal()

    @staticmethod
    def init_db():
        """Initialize database tables"""
        Base.metadata.create_all(bind=engine)

    def get_ongoing_votes(self) -> Dict[str, Any]:
        """Get all ongoing votes"""
        session = self._get_session()
        votes = session.query(OngoingVote).all()
        if self._session is None:
            session.close()
        return {
            vote.proposal_id: {
                "draft": vote.draft,
                "end_time": vote.end_time,
                "title": vote.title,
                "channel_id": vote.channel_id,
                "thread_id": vote.thread_id,
                "message_id": vote.message_id,
            }
            for vote in votes
        }

    def get_ongoing_vote(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """Get an ongoing vote by proposal ID"""
        session = self._get_session()
        vote = session.query(OngoingVote).filter_by(proposal_id=proposal_id).first()
        if self._session is None:
            session.close()
        if not vote:
            return None
        return {
            "proposal_id": vote.proposal_id,
            "draft": vote.draft,
            "end_time": vote.end_time,
            "title": vote.title,
            "channel_id": vote.channel_id,
            "thread_id": vote.thread_id,
            "message_id": vote.message_id,
        }

    def save_ongoing_vote(self, vote_data: Dict[str, Any]) -> None:
        """Save an ongoing vote to the database"""
        session = self._get_session()
        vote = OngoingVote(
            proposal_id=vote_data["proposal_id"],
            draft=vote_data["draft"],
            end_time=vote_data["end_time"],
            title=vote_data["title"],
            channel_id=vote_data["channel_id"],
            thread_id=vote_data["thread_id"],
            message_id=vote_data["message_id"],
        )
        session.add(vote)
        session.commit()
        if self._session is None:
            session.close()

    def get_posted_events(self) -> List[int]:
        """Get all posted event IDs"""
        session = self._get_session()
        events = session.query(Event.event_id).filter(Event.posted_at.isnot(None)).all()
        if self._session is None:
            session.close()
        return [event.event_id for event in events]

    def save_posted_event(self, event_id: int, guild_id: int):
        """Save a posted event"""
        session = self._get_session()
        event = Event(
            event_id=event_id, guild_id=guild_id, posted_at=datetime.now().timestamp()
        )
        session.add(event)
        session.commit()
        if self._session is None:
            session.close()

    def get_notified_events(self) -> Dict[int, float]:
        """Get all notified events"""
        session = self._get_session()
        events = session.query(Event).filter(Event.notified_at.isnot(None)).all()
        if self._session is None:
            session.close()
        return {event.event_id: event.notified_at for event in events}

    def save_notified_event(self, event_id: int, guild_id: int, notified_at: float):
        """Save a notified event"""
        session = self._get_session()
        event = session.query(Event).filter_by(event_id=event_id).first()
        if event:
            event.notified_at = notified_at
        else:
            event = Event(event_id=event_id, guild_id=guild_id, notified_at=notified_at)
            session.add(event)
        session.commit()
        if self._session is None:
            session.close()

    def get_contributors_and_emoji_dicts(self):
        """Get contributors and emoji dictionaries"""
        session = self._get_session()
        contributors = session.query(Contributor).all()

        result = {"Bloom Studio": [], "Bloom Collective": []}
        emoji_dicts = {"Bloom Studio": {}, "Bloom Collective": {}}

        for c in contributors:
            result[c.server_name].append({"uid": c.uid, "note": c.note})
            if c.emoji_id:
                emoji_dicts[c.server_name][c.emoji_id] = c.uid

        if self._session is None:
            session.close()

        return result, emoji_dicts
