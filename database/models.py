from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, BigInteger, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from logger.logger import logger

# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Only check for individual connection parameters if not in testing mode and no DATABASE_URL
if not DATABASE_URL and os.getenv("TESTING") != "true":
    # Check for individual database connection parameters
    required_vars = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
        
    # Construct URL from environment variables
    DATABASE_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# For testing, use SQLite if no DATABASE_URL is provided
if not DATABASE_URL and os.getenv("TESTING") == "true":
    DATABASE_URL = "sqlite:///:memory:"

# Heroku specific: convert postgres:// to postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with appropriate settings based on database type
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(DATABASE_URL)
else:
    # PostgreSQL settings
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=1800
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Config(Base):
    __tablename__ = "configs"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)

class Contributor(Base):
    __tablename__ = "contributors"
    
    id = Column(Integer, primary_key=True)
    uid = Column(String)
    note = Column(String)
    server_name = Column(String)
    emoji_id = Column(String)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True)
    event_id = Column(BigInteger, unique=True)
    guild_id = Column(BigInteger)
    posted_at = Column(Float)
    notified_at = Column(Float)

class OngoingVote(Base):
    __tablename__ = "ongoing_votes"
    
    id = Column(Integer, primary_key=True)
    proposal_id = Column(String, unique=True)
    draft = Column(JSON)
    end_time = Column(Float)
    title = Column(String)
    channel_id = Column(String)
    thread_id = Column(String)
    message_id = Column(String)

class ConcludedVote(Base):
    __tablename__ = "concluded_votes"
    
    id = Column(Integer, primary_key=True)
    proposal_id = Column(String, unique=True)
    draft = Column(JSON)
    title = Column(String)
    channel_id = Column(String)
    thread_id = Column(String)
    message_id = Column(String)
    yes_count = Column(Integer)
    no_count = Column(Integer)
    abstain_count = Column(Integer)
    passed = Column(Boolean)
    concluded_at = Column(Float)
    snapshot_url = Column(String, nullable=True)