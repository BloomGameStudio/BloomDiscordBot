#!/usr/bin/env python3
from database.models import Base, engine
from logger.logger import logger


def init_db():
    """Initialize database tables"""
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully")


if __name__ == "__main__":
    init_db()
