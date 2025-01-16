from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bloom:bloom@localhost:5432/bloombot")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
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