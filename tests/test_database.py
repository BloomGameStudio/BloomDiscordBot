import pytest
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Contributor, Event, OngoingVote, ConcludedVote
from database.service import DatabaseService

@pytest.fixture(scope="function")
def test_db():
    """Create a test database and tables"""
    # Use SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(engine)

class TestContributors:
    def test_create_contributor(self, test_db):
        """Test creating a new contributor"""
        contributor = Contributor(
            uid="123456789",
            note="Test Contributor",
            server_name="Test Server",
            emoji_id="🌟"
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
            emoji_id="🌟"
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
            emoji_id="🌟"
        )
        test_db.add(contributor)
        test_db.commit()
        
        test_db.delete(contributor)
        test_db.commit()
        
        assert test_db.query(Contributor).count() == 0

class TestEvents:
    def test_create_event(self, test_db):
        """Test creating a new event"""
        event = Event(
            event_id=123456789,
            guild_id=987654321,
            posted_at=datetime.now().timestamp(),
            notified_at=datetime.now().timestamp()
        )
        test_db.add(event)
        test_db.commit()
        
        saved = test_db.query(Event).first()
        assert saved.event_id == 123456789
        assert saved.guild_id == 987654321
        assert saved.posted_at is not None
        assert saved.notified_at is not None
    
    def test_update_event(self, test_db):
        """Test updating an existing event"""
        event = Event(
            event_id=123456789,
            guild_id=987654321,
            posted_at=100.0
        )
        test_db.add(event)
        test_db.commit()
        
        new_time = 200.0
        event.posted_at = new_time
        test_db.commit()
        
        updated = test_db.query(Event).first()
        assert updated.posted_at == new_time

class TestOngoingVotes:
    def test_create_vote(self, test_db):
        """Test creating a new ongoing vote"""
        vote = OngoingVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            end_time=datetime.now().timestamp(),
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789"
        )
        test_db.add(vote)
        test_db.commit()
        
        saved = test_db.query(OngoingVote).first()
        assert saved.proposal_id == "test123"
        assert saved.draft["title"] == "Test Proposal"
        assert saved.title == "Test Vote"
    
    def test_update_vote(self, test_db):
        """Test updating an ongoing vote"""
        vote = OngoingVote(
            proposal_id="test123",
            draft={"title": "Test Proposal", "content": "Test Content"},
            end_time=datetime.now().timestamp(),
            title="Test Vote",
            channel_id="123",
            thread_id="456",
            message_id="789"
        )
        test_db.add(vote)
        test_db.commit()
        
        vote.title = "Updated Vote"
        test_db.commit()
        
        updated = test_db.query(OngoingVote).first()
        assert updated.title == "Updated Vote"

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
            concluded_at=datetime.now().timestamp(),
            snapshot_url="https://snapshot.org/test"
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
            concluded_at=datetime.now().timestamp()
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
            message_id="789"
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
            event_id=123456789,
            guild_id=987654321,
            posted_at=datetime.now().timestamp()
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
            notified_at=datetime.now().timestamp()
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
            "message_id": "789"
        }
        
        db_service = DatabaseService(session=test_db)
        db_service.save_concluded_vote(
            proposal_data=proposal_data,
            yes_count=5,
            no_count=2,
            abstain_count=1,
            passed=True,
            snapshot_url="https://snapshot.org/test"
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
            concluded_at=datetime.now().timestamp()
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
            concluded_at=datetime.now().timestamp()
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
            concluded_at=datetime.now().timestamp()
        )
        test_db.add(passed_vote)
        test_db.add(failed_vote)
        test_db.commit()
        
        db_service = DatabaseService(session=test_db)
        votes = db_service.get_concluded_votes(passed_only=True)
        assert "passed123" in votes
        assert "failed123" not in votes 