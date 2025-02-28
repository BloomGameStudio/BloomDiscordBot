#!/usr/bin/env python3
from database.models import SessionLocal, Base, Config, engine
from logger.logger import logger


def init_db():
    """Initialize database tables"""
    logger.info("Initializing database tables")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        for key, value in [("next_budget_id", "1"), ("next_governance_id", "1")]:
            if not db.query(Config).filter(Config.key == key).first():
                db.add(Config(key=key, value=value))

        db.commit()
    except Exception as e:
        logger.error(f"Error initializing config values: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info("Database tables initialized successfully")


if __name__ == "__main__":
    init_db()
