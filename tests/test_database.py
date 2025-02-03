import pytest
import os
from datetime import datetime
from sqlalchemy import create_engine, JSON, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator
from database.models import Base, Contributor, Event, OngoingVote, ConcludedVote
from database.service import DatabaseService
import time
import json

TEST_DB_URL = "sqlite:///:memory:"


class JSONType(TypeDecorator):
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment for DatabaseService"""
    engine = create_engine(TEST_DB_URL)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    import database.service

    database.service.SessionLocal = TestingSessionLocal
    database.service.get_db = lambda: TestingSessionLocal()

    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def test_db():
    """Create an in-memory database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestContributors:
    def test_create_contributor(self, test_db):
        """Test creating a new contributor"""
        contributor = Contributor(
            uid="123456789",
            note="Test Contributor",
            server_name="Test Server",
            emoji_id="🌟",
        )
        test_db.add(contributor)
        test_db.commit()

        saved = test_db.query(Contributor).first()
        assert saved.uid == "123456789"
        assert saved.note == "Test Contributor"
        assert saved.server_name == "Test Server"
        assert saved.emoji_id == "🌟"

    def test_update_contributor(self, test_db):
        """Test updating an existing contributor"""
        contributor = Contributor(
            uid="123456789",
            note="Original Note",
            server_name="Test Server",
            emoji_id="🌟",
        )
        test_db.add(contributor)
        test_db.commit()

        contributor.note = "Updated Note"
        test_db.commit()

        updated = test_db.query(Contributor).first()
        assert updated.note == "Updated Note"

    def test_delete_contributor(self, test_db):
        """Test deleting a contributor"""
        contributor = Contributor(
            uid="123456789",
            note="Test Contributor",
            server_name="Test Server",
            emoji_id="🌟",
        )
        test_db.add(contributor)
        test_db.commit()

        test_db.delete(contributor)
        test_db.commit()

        assert test_db.query(Contributor).count() == 0


class TestEvents:
    def test_create_event(self, test_db):
        """Test creating a new event"""
        current_time = int(datetime.now().timestamp())
        event = Event(
            event_id=123456789,
            guild_id=987654321,
            posted_at=current_time,
            notified_at=current_time,
        )
        test_db.add(event)
        test_db.commit()

        saved = test_db.query(Event).first()
        assert saved.event_id == 123456789
        assert saved.guild_id == 987654321
        assert isinstance(saved.posted_at, int)
        assert isinstance(saved.notified_at, int)

    def test_update_event(self, test_db):
        """Test updating an existing event"""
        event = Event(
            event_id=123456789,
            guild_id=987654321,
            posted_at=1234567890,  # Use integer timestamp
        )
        test_db.add(event)
        test_db.commit()

        new_time = 1234567891  # Use integer timestamp
        event.posted_at = new_time
        test_db.commit()

        updated = test_db.query(Event).first()
        assert updated.posted_at == new_time
        assert isinstance(updated.posted_at, int)


class TestOngoingVotes:
    def test_create_vote(self, test_db):
        """Test creating a new ongoing vote"""
        current_time = int(datetime.now().timestamp())  # Convert to integer timestamp
        vote = OngoingVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            end_time=current_time,
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
        )
        test_db.add(vote)
        test_db.commit()

        saved = test_db.query(OngoingVote).first()
        assert saved.proposal_id == "test123"
        assert saved.draft["title"] == "Test Proposal"
        assert saved.title == "Test Vote"
        assert isinstance(saved.end_time, int)

    def test_update_vote(self, test_db):
        """Test updating an ongoing vote"""
        current_time = int(datetime.now().timestamp())  # Convert to integer timestamp
        vote = OngoingVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            end_time=current_time,
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
        )
        test_db.add(vote)
        test_db.commit()

        vote.title = "Updated Vote"
        test_db.commit()

        updated = test_db.query(OngoingVote).first()
        assert updated.title == "Updated Vote"
        assert isinstance(updated.end_time, int)


class TestConcludedVotes:
    def test_create_concluded_vote(self, test_db):
        """Test creating a new concluded vote"""
        vote = ConcludedVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            concluded_at=int(datetime.now().timestamp()),
            snapshot_url="https://snapshot.org/test",
        )
        test_db.add(vote)
        test_db.commit()

        saved = test_db.query(ConcludedVote).first()
        assert saved.proposal_id == "test123"
        assert saved.draft["title"] == "Test Proposal"
        assert saved.title == "Test Vote"
        assert saved.yes_count == 5
        assert saved.passed is True
        assert saved.snapshot_url == "https://snapshot.org/test"

    def test_update_concluded_vote(self, test_db):
        """Test updating a concluded vote"""
        vote = ConcludedVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            concluded_at=int(datetime.now().timestamp()),
        )
        test_db.add(vote)
        test_db.commit()

        vote.yes_count = 10
        vote.passed = False
        test_db.commit()

        updated = test_db.query(ConcludedVote).first()
        assert updated.yes_count == 10
        assert updated.passed is False


class TestDatabaseService:
    def test_get_ongoing_votes(self, test_db):
        """Test retrieving ongoing votes"""
        vote = OngoingVote(
            proposal_id="test123",
            draft={"title": "Test Proposal"},
            end_time=datetime.now().timestamp(),
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
        )
        test_db.add(vote)
        test_db.commit()

        db_service = DatabaseService(session=test_db)
        votes = db_service.get_ongoing_votes()
        assert "test123" in votes
        assert votes["test123"]["title"] == "Test Vote"

    def test_get_posted_events(self, test_db):
        """Test retrieving posted events"""
        event = Event(
            event_id=123456789, guild_id=987654321, posted_at=datetime.now().timestamp()
        )
        test_db.add(event)
        test_db.commit()

        db_service = DatabaseService(session=test_db)
        events = db_service.get_posted_events()
        assert 123456789 in events

    def test_get_notified_events(self, test_db):
        """Test retrieving notified events"""
        event = Event(
            event_id=123456789,
            guild_id=987654321,
            notified_at=datetime.now().timestamp(),
        )
        test_db.add(event)
        test_db.commit()

        db_service = DatabaseService(session=test_db)
        events = db_service.get_notified_events()
        assert 123456789 in events

    def test_save_concluded_vote(self, test_db):
        """Test saving a concluded vote"""
        proposal_data = {
            "proposal_id": "test123",
            "draft": {"title": "Test Proposal"},
            "title": "Test Vote",
            "channel_id": "123",
            "thread_id": "456",
            "message_id": "789",
        }

        db_service = DatabaseService(session=test_db)
        db_service.save_concluded_vote(
            proposal_data=proposal_data,
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            snapshot_url="https://snapshot.org/test",
        )

        saved = test_db.query(ConcludedVote).first()
        assert saved.proposal_id == "test123"
        assert saved.yes_count == 5
        assert saved.passed is True
        assert saved.snapshot_url == "https://snapshot.org/test"

    def test_get_concluded_votes(self, test_db):
        """Test retrieving concluded votes"""
        vote = ConcludedVote(
            proposal_id="test123",
            draft={"title": "Test Proposal"},
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            concluded_at=int(datetime.now().timestamp()),
        )
        test_db.add(vote)
        test_db.commit()

        db_service = DatabaseService(session=test_db)
        votes = db_service.get_concluded_votes()
        assert "test123" in votes
        assert votes["test123"]["title"] == "Test Vote"
        assert votes["test123"]["passed"] is True

    def test_get_concluded_votes_passed_only(self, test_db):
        """Test retrieving only passed concluded votes"""
        # Add a passed vote
        passed_vote = ConcludedVote(
            proposal_id="passed123",
            draft={"title": "Passed Proposal"},
            title="Passed Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            concluded_at=int(datetime.now().timestamp()),
        )
        # Add a failed vote
        failed_vote = ConcludedVote(
            proposal_id="failed123",
            draft={"title": "Failed Proposal"},
            title="Failed Vote",
            channel_id="123",
            thread_id="456",
            message_id="789",
            yes_count=2,
            no_count=5,
            abstain_count=1,
            passed=False,
            concluded_at=int(datetime.now().timestamp()),
        )
        test_db.add(passed_vote)
        test_db.add(failed_vote)
        test_db.commit()

        db_service = DatabaseService(session=test_db)
        votes = db_service.get_concluded_votes(passed_only=True)
        assert "passed123" in votes
        assert "failed123" not in votes

    def test_save_event(self, test_db):
        """Test saving an event"""
        current_time = int(time.time())
        db_service = DatabaseService(session=test_db)

        # Test creating new event
        db_service.save_event(
            event_id=123456789, guild_id=987654321, posted_at=current_time
        )

        saved = test_db.query(Event).first()
        assert saved.event_id == 123456789
        assert saved.posted_at == current_time

        # Test updating existing event
        new_time = current_time + 3600
        db_service.save_event(
            event_id=123456789, guild_id=987654321, notified_at=new_time
        )

        updated = test_db.query(Event).first()
        assert updated.event_id == 123456789
        assert updated.posted_at == current_time
        assert updated.notified_at == new_time
