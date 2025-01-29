import pytest
import json
import os
import logging
from scripts.migrate_to_db import (
    migrate_contributors,
    load_json_file,
    migrate_events,
    migrate_ongoing_votes,
)
from database.models import Contributor, Event, OngoingVote
from tests.test_database import test_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_migrate_contributors(test_db):
    """Test migrating contributors from contributors.json to database"""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "contributors.json"
    )
    contributors_data = load_json_file(data_path)

    if not contributors_data:
        logger.info("No contributors data found in contributors.json")
        assert migrate_contributors(test_db, {}) == 0
        return

    result = migrate_contributors(test_db, contributors_data)
    assert result >= 0

    contributors = test_db.query(Contributor).all()
    assert len(contributors) == result

    for contributor in contributors:
        assert contributor.uid
        assert contributor.server_name
        assert contributor.note


def test_migrate_events(test_db):
    """Test migrating events from posted_events.json"""
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    events_data = load_json_file(os.path.join(data_path, "events.json"))

    if not events_data:
        logger.info("No events data found in events.json")
        assert migrate_events(test_db, {}) == 0
        return

    result = migrate_events(test_db, events_data)
    assert result >= 0


def test_migrate_ongoing_votes(test_db):
    """Test migrating votes from ongoing_votes.json"""
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "data", "ongoing_votes.json"
    )
    votes_data = load_json_file(data_path)

    if not votes_data:
        logger.info("No ongoing votes data found in ongoing_votes.json")
        assert migrate_ongoing_votes(test_db, {}) == 0
        return

    result = migrate_ongoing_votes(test_db, votes_data)
    assert result >= 0


def test_migrate_empty_data(test_db):
    """Test migrating empty data"""
    empty_data = {}
    assert migrate_contributors(test_db, empty_data) == 0
    assert test_db.query(Contributor).count() == 0


def test_migrate_invalid_data(test_db):
    """Test migrating invalid data doesn't crash and returns 0"""
    invalid_data = {"invalid": "data"}
    assert migrate_contributors(test_db, invalid_data) == 0
