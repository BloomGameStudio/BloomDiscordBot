from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from datetime import datetime
from .models import SessionLocal, Contributor, Event, OngoingVote, ConcludedVote
from logger.logger import logger
import time


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
        logger.info(
            "DatabaseService initialized with %s",
            "test session" if session else "default session",
        )

    def _get_session(self):
        """Get database session - uses provided test session or creates new one"""
        if self._session is not None:
            logger.debug("Using provided test session")
            return self._session
        logger.debug("Creating new database session")
        return SessionLocal()

    def get_ongoing_votes(self) -> Dict[str, Any]:
        """Get all ongoing votes"""
        logger.info("Retrieving all ongoing votes")
        session = self._get_session()
        try:
            votes = session.query(OngoingVote).all()
            result = {}
            for vote in votes:
                result[vote.proposal_id] = {
                    "proposal_id": vote.proposal_id,
                    "draft": vote.draft,
                    "end_time": vote.end_time,
                    "title": vote.title,
                    "channel_id": vote.channel_id,
                    "thread_id": vote.thread_id,
                    "message_id": vote.message_id,
                    "yes_count": getattr(vote, "yes_count", 0),
                    "no_count": getattr(vote, "no_count", 0),
                    "abstain_count": getattr(vote, "abstain_count", 0),
                }
            logger.info(f"Found {len(result)} ongoing votes")
            return result
        except Exception as e:
            logger.error(f"Error retrieving ongoing votes: {e}")
            return {}
        finally:
            if self._session is None:
                session.close()

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

    def save_ongoing_vote(self, proposal_data: dict) -> None:
        """Save an ongoing vote to the database"""
        if not proposal_data or "proposal_id" not in proposal_data:
            logger.error(
                "Cannot save ongoing vote: missing proposal_id in proposal data"
            )
            return

        logger.info(
            "Saving ongoing vote for proposal %s", proposal_data.get("proposal_id")
        )
        session = self._get_session()
        try:
            existing_vote = (
                session.query(OngoingVote)
                .filter_by(proposal_id=proposal_data["proposal_id"])
                .first()
            )

            if existing_vote:
                existing_vote.draft = proposal_data.get("draft", {})
                existing_vote.end_time = proposal_data.get("end_time", 0)
                existing_vote.title = proposal_data.get("title", "")
                existing_vote.channel_id = proposal_data.get("channel_id", "")
                existing_vote.thread_id = proposal_data.get("thread_id", "")
                existing_vote.message_id = proposal_data.get("message_id", "")
                logger.info("Updated existing ongoing vote")
            else:
                vote = OngoingVote(
                    proposal_id=proposal_data["proposal_id"],
                    draft=proposal_data.get("draft", {}),
                    end_time=proposal_data.get("end_time", 0),
                    title=proposal_data.get("title", ""),
                    channel_id=proposal_data.get("channel_id", ""),
                    thread_id=proposal_data.get("thread_id", ""),
                    message_id=proposal_data.get("message_id", ""),
                )
                session.add(vote)
                logger.info("Created new ongoing vote")

            session.commit()
        except Exception as e:
            logger.error(f"Error saving ongoing vote: {e}")
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def get_posted_events(self) -> Dict[int, Event]:
        """Get all posted events from the database"""
        logger.info("Getting posted events")
        session = self._get_session()
        try:
            events = session.query(Event).filter(Event.posted_at.isnot(None)).all()
            return {event.event_id: event for event in events}
        finally:
            if self._session is None:
                session.close()

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

    def get_notified_events(self) -> Dict[int, Event]:
        """Get all notified events from the database"""
        logger.info("Getting notified events")
        session = self._get_session()
        try:
            events = session.query(Event).filter(Event.notified_at.isnot(None)).all()
            return {event.event_id: event for event in events}
        finally:
            if self._session is None:
                session.close()

    def save_notified_event(self, event_id: int, guild_id: int, notified_at: int):
        """Save a notified event"""
        session = self._get_session()
        event = session.query(Event).filter_by(event_id=event_id).first()
        if event:
            event.notified_at = int(notified_at)
        else:
            event = Event(
                event_id=event_id, guild_id=guild_id, notified_at=int(notified_at)
            )
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

    def save_concluded_vote(
        self,
        proposal_data: dict,
        yes_count: int,
        no_count: int,
        abstain_count: int,
        passed: bool,
        snapshot_url: Optional[str] = None,
    ) -> None:
        """Save a concluded vote to the database"""
        session = self._get_session()
        try:
            concluded_vote = ConcludedVote(
                proposal_id=proposal_data["proposal_id"],
                draft=proposal_data["draft"],
                title=proposal_data["title"],
                channel_id=proposal_data["channel_id"],
                thread_id=proposal_data["thread_id"],
                message_id=proposal_data["message_id"],
                yes_count=yes_count,
                no_count=no_count,
                abstain_count=abstain_count,
                passed=passed,
                snapshot_url=snapshot_url,
                concluded_at=int(time.time()),
            )
            session.add(concluded_vote)
            session.commit()
            logger.info(
                f"Successfully saved concluded vote for proposal {proposal_data['proposal_id']}"
            )
        except Exception as e:
            logger.error(f"Error saving concluded vote: {e}")
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def get_concluded_votes(self, passed_only: bool = False) -> Dict[str, Any]:
        """Get all concluded votes from the database"""
        logger.info(
            "Getting concluded votes%s", " (passed only)" if passed_only else ""
        )
        session = self._get_session()
        try:
            query = session.query(ConcludedVote)
            if passed_only:
                query = query.filter(ConcludedVote.passed == True)

            votes = query.order_by(ConcludedVote.concluded_at.desc()).all()
            return {
                vote.proposal_id: {
                    "draft": vote.draft,
                    "title": vote.title,
                    "yes_count": vote.yes_count,
                    "no_count": vote.no_count,
                    "abstain_count": vote.abstain_count,
                    "passed": vote.passed,
                    "concluded_at": vote.concluded_at,
                    "snapshot_url": vote.snapshot_url,
                }
                for vote in votes
            }
        finally:
            if self._session is None:
                session.close()

    def update_contributor_in_db(
        self, guild_id: int, uid: str, note: str, emoji_id: str
    ) -> None:
        """Update or create a contributor in the database"""
        logger.info(f"Updating contributor {uid} in guild {guild_id}")
        session = self._get_session()
        try:
            contributor = (
                session.query(Contributor)
                .filter_by(server_name=str(guild_id), uid=uid)
                .first()
            )
            if contributor:
                contributor.note = note
                contributor.emoji_id = emoji_id
            else:
                contributor = Contributor(
                    server_name=str(guild_id), uid=uid, note=note, emoji_id=emoji_id
                )
                session.add(contributor)
            session.commit()
            logger.info("Successfully updated contributor")
        except Exception as e:
            logger.error(f"Error updating contributor: {e}")
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def get_contributors_from_db(self, server_id: int = None) -> List[Contributor]:
        """Get contributors from database, optionally filtered by server"""
        logger.info(
            "Getting contributors for server: %s", server_id if server_id else "all"
        )
        session = self._get_session()
        try:
            query = session.query(Contributor)
            if server_id:
                query = query.filter_by(server_name=str(server_id))
            return query.all()
        finally:
            if self._session is None:
                session.close()

    def remove_contributor_from_db(self, guild_id: int, uid: str) -> None:
        """Remove a contributor from the database"""
        session = self._get_session()
        try:
            contributor = (
                session.query(Contributor)
                .filter_by(server_name=str(guild_id), uid=uid)
                .first()
            )

            if not contributor:
                logger.warning(
                    f"No contributor found with uid={uid} in server={guild_id}"
                )
                return

            session.delete(contributor)
            session.commit()
            logger.info(
                f"Successfully removed contributor with uid={uid} from server={guild_id}"
            )
        except Exception as e:
            logger.error(f"Error removing contributor: {e}")
            raise
        finally:
            if self._session is None:
                session.close()

    def remove_ongoing_vote(self, proposal_id: str) -> None:
        """Remove an ongoing vote from the database"""
        logger.info("Removing ongoing vote with proposal_id: %s", proposal_id)
        session = self._get_session()
        try:
            session.query(OngoingVote).filter_by(proposal_id=proposal_id).delete()
            session.commit()
            logger.info("Successfully removed ongoing vote")
        except Exception as e:
            logger.error("Error removing ongoing vote: %s", str(e))
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def save_event(
        self,
        event_id: int,
        guild_id: int,
        posted_at: Optional[int] = None,
        notified_at: Optional[int] = None,
    ) -> None:
        """Save or update an event"""
        logger.info("Saving event with id: %s", event_id)
        session = self._get_session()
        try:
            event = session.query(Event).filter_by(event_id=event_id).first()
            if event:
                logger.info("Updating existing event")
                if posted_at is not None:
                    event.posted_at = posted_at
                if notified_at is not None:
                    event.notified_at = notified_at
            else:
                logger.info("Creating new event")
                event = Event(
                    event_id=event_id,
                    guild_id=guild_id,
                    posted_at=posted_at,
                    notified_at=notified_at,
                )
                session.add(event)
            session.commit()
            logger.info("Successfully saved event")
        except Exception as e:
            logger.error("Error saving event: %s", str(e))
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def get_all_contributors(self) -> List[Contributor]:
        """Get all contributors from the database"""
        logger.info("Getting all contributors")
        session = self._get_session()
        try:
            contributors = session.query(Contributor).all()
            return contributors
        finally:
            if self._session is None:
                session.close()

    def get_all_events(self) -> List[Event]:
        """Get all events from the database"""
        logger.info("Getting all events")
        session = self._get_session()
        try:
            events = session.query(Event).all()
            return events
        finally:
            if self._session is None:
                session.close()

    def migrate_contributors(self, contributors_data: dict) -> int:
        """Migrate contributors from JSON to database"""
        logger.info("Migrating contributors")
        session = self._get_session()
        try:
            session.query(Contributor).delete()
            session.commit()

            total_migrated = 0
            if not contributors_data.get("servers"):
                logger.warning("No valid contributors data found")
                return 0

            for server_id, server_data in contributors_data["servers"].items():
                emoji_dict = server_data.get("emoji_dictionary", {})
                for contributor in server_data.get("contributors", []):
                    emoji_id = None
                    for emoji, uid in emoji_dict.items():
                        if uid == contributor["uid"]:
                            emoji_id = emoji
                            break

                    new_contributor = Contributor(
                        uid=contributor["uid"],
                        note=contributor["note"],
                        server_name=server_id,
                        emoji_id=emoji_id,
                    )
                    session.add(new_contributor)
                    total_migrated += 1

            session.commit()
            logger.info(f"Successfully migrated {total_migrated} contributors")
            return total_migrated
        except Exception as e:
            logger.error(f"Error migrating contributors: {e}")
            session.rollback()
            return 0
        finally:
            if self._session is None:
                session.close()

    def migrate_events(self, events_data: dict) -> int:
        """Migrate events from JSON to database"""
        logger.info("Migrating events")
        session = self._get_session()
        try:
            session.query(Event).delete()
            session.commit()

            total_migrated = 0
            for event_id, event_data in events_data.items():
                new_event = Event(
                    event_id=int(event_id),
                    guild_id=event_data.get("guild_id", 0),
                    posted_at=event_data.get("posted_at"),
                    notified_at=event_data.get("notified_at"),
                )
                session.add(new_event)
                total_migrated += 1

            session.commit()
            logger.info(f"Successfully migrated {total_migrated} events")
            return total_migrated
        except Exception as e:
            logger.error(f"Error migrating events: {e}")
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()

    def migrate_ongoing_votes(self, votes_data: dict) -> int:
        """Migrate ongoing votes from JSON to database"""
        logger.info("Migrating ongoing votes")
        session = self._get_session()
        try:
            session.query(OngoingVote).delete()
            session.commit()

            total_migrated = 0
            for proposal_id, vote_data in votes_data.items():
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
            logger.info(f"Successfully migrated {total_migrated} ongoing votes")
            return total_migrated
        except Exception as e:
            logger.error(f"Error migrating ongoing votes: {e}")
            session.rollback()
            raise
        finally:
            if self._session is None:
                session.close()
