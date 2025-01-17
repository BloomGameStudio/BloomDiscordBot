import os
import sys

# Set test environment variables first
os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Now import test dependencies
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, SessionLocal

@pytest.fixture(scope="function")
def test_engine():
    """Create a fresh database engine for each test."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="function")
def test_session(test_engine):
    """Create a new database session for each test."""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(test_engine)

@pytest.fixture(scope="function")
def test_db(test_session):
    """Provide the database session to tests."""
    return test_session

@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment for DatabaseService"""
    # Override the SessionLocal to use in-memory SQLite
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    
    # Replace the global SessionLocal with our test version
    import database.service
    database.service.SessionLocal = TestingSessionLocal
    database.service.get_db = lambda: TestingSessionLocal()
    
    yield
    
    # Cleanup
    Base.metadata.drop_all(engine) 