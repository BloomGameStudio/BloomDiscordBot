from sqlalchemy import inspect


def test_table_exists(test_db):
    """Test that tables exist after initial creation"""
    inspector = inspect(test_db.bind)
    tables = inspector.get_table_names()
    assert "ongoing_votes" in tables
    assert "events" in tables
    assert "contributors" in tables
    assert "concluded_votes" in tables


def test_columns_exist(test_db):
    """Test that expected columns exist in tables"""
    inspector = inspect(test_db.bind)

    ongoing_votes_columns = {
        col["name"] for col in inspector.get_columns("ongoing_votes")
    }
    assert "proposal_id" in ongoing_votes_columns
    assert "draft" in ongoing_votes_columns
    assert "end_time" in ongoing_votes_columns

    events_columns = {col["name"] for col in inspector.get_columns("events")}
    assert "event_id" in events_columns
    assert "guild_id" in events_columns
    assert "posted_at" in events_columns

    contributors_columns = {
        col["name"] for col in inspector.get_columns("contributors")
    }
    assert "uid" in contributors_columns
    assert "note" in contributors_columns
    assert "server_name" in contributors_columns

    concluded_votes_columns = {
        col["name"] for col in inspector.get_columns("concluded_votes")
    }
    assert "proposal_id" in concluded_votes_columns
    assert "draft" in concluded_votes_columns
    assert "title" in concluded_votes_columns
    assert "yes_count" in concluded_votes_columns
    assert "no_count" in concluded_votes_columns
    assert "abstain_count" in concluded_votes_columns
    assert "passed" in concluded_votes_columns
    assert "concluded_at" in concluded_votes_columns
    assert "snapshot_url" in concluded_votes_columns
