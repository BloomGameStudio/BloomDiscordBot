from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from .models import SessionLocal, Config, Contributor, Event, OngoingVote, Base, engine
from logger.logger import logger


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
        logger.info("DatabaseService initialized with %s", "test session" if session else "default session")

    def _get_session(self):
        """Get database session - uses provided test session or creates new one"""
        if self._session is not None:
            logger.debug("Using provided test session")
            return self._session
        logger.debug("Creating new database session")
        return SessionLocal()

    @staticmethod
    def init_db():
        """Initialize database tables"""
        logger.info("Initializing database tables")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully")

    def get_ongoing_votes(self) -> Dict[str, Any]:
        """Get all ongoing votes"""
        logger.info("Retrieving all ongoing votes")
        session = self._get_session()
        votes = session.query(OngoingVote).all()
        if self._session is None:
            session.close()
        logger.info("Found %d ongoing votes", len(votes))
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
        logger.info("Retrieving ongoing vote with proposal_id: %s", proposal_id)
        session = self._get_session()
        vote = session.query(OngoingVote).filter_by(proposal_id=proposal_id).first()
        if self._session is None:
            session.close()
        if not vote:
            logger.info("No ongoing vote found with proposal_id: %s", proposal_id)
            return None
        logger.info("Found ongoing vote: %s", vote.title)
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
        """Save or update an ongoing vote"""
        logger.info("Saving ongoing vote with proposal_id: %s", vote_data.get("proposal_id"))
        session = self._get_session()
        try:
            vote = session.query(OngoingVote).filter_by(proposal_id=vote_data["proposal_id"]).first()
            if vote:
                logger.info("Updating existing ongoing vote")
                for key, value in vote_data.items():
                    setattr(vote, key, value)
            else:
                logger.info("Creating new ongoing vote")
                vote = OngoingVote(**vote_data)
                session.add(vote)
            session.commit()
            logger.info("Successfully saved ongoing vote")
        except Exception as e:
            logger.error("Error saving ongoing vote: %s", str(e))
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def get_posted_events(self) -> List[str]:
        """Get list of posted event IDs"""
        logger.info("Retrieving all posted events")
        session = self._get_session()
        events = session.query(Event).filter(Event.posted_at.isnot(None)).all()
        if self._session is None:
            session.close()
        event_ids = [str(event.event_id) for event in events]
        logger.info("Found %d posted events", len(event_ids))
        return event_ids

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

    def get_notified_events(self) -> Dict[str, float]:
        """Get dictionary of notified event IDs and their notification timestamps"""
        logger.info("Retrieving all notified events")
        session = self._get_session()
        events = session.query(Event).filter(Event.notified_at.isnot(None)).all()
        if self._session is None:
            session.close()
        event_dict = {str(event.event_id): event.notified_at for event in events}
        logger.info("Found %d notified events", len(event_dict))
        return event_dict

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
