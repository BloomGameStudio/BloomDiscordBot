import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    BigInteger,
    JSON,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker


def get_database_url():
    if os.getenv("DATABASE_URL"):
        url = os.getenv("DATABASE_URL")
        return (
            url.replace("postgres://", "postgresql://", 1)
            if url.startswith("postgres://")
            else url
        )

    DB_USER = os.getenv("DB_USER", "bloom")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME", "bloombot")
    DB_HOST = os.getenv("DB_HOST", "localhost")

    if not DB_PASSWORD:
        raise ValueError("DB_PASSWORD environment variable is required")

    return f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"


DATABASE_URL = os.getenv("DATABASE_URL") or get_database_url()

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL, pool_size=5, max_overflow=10, pool_timeout=30, pool_recycle=1800
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
    posted_at = Column(BigInteger)
    notified_at = Column(BigInteger)


class OngoingVote(Base):
    __tablename__ = "ongoing_votes"

    id = Column(Integer, primary_key=True)
    proposal_id = Column(String, unique=True)
    draft = Column(JSON)
    end_time = Column(BigInteger)
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
    concluded_at = Column(BigInteger)
    snapshot_url = Column(String, nullable=True)
