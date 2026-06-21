"""
Serverless Database Service

Abstraction layer for database operations.
Supports both SQLite (local) and Azure SQL/Cosmos DB (production).
"""

from typing import List, Dict, Any, Optional
import os


class ServerlessDatabaseService:
    """Database service for serverless functions."""

    def __init__(self, db_type: str = "sqlite"):
        """
        Initialize database service.

        Args:
            db_type: "sqlite", "azure_sql", or "cosmos"
        """
        self.db_type = db_type or os.getenv("DB_TYPE", "sqlite")

        if self.db_type == "sqlite":
            self._init_sqlite()
        elif self.db_type == "azure_sql":
            self._init_azure_sql()
        elif self.db_type == "cosmos":
            self._init_cosmos()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")

    def _init_sqlite(self):
        """Initialize SQLite connection (for local dev)."""
        import sqlite3

        self.db_path = os.getenv("SQLITE_DB_PATH", "bloom.db")
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def _init_azure_sql(self):
        """Initialize Azure SQL connection."""
        import pyodbc

        connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("AZURE_SQL_CONNECTION_STRING not set")

        self.connection = pyodbc.connect(connection_string)

    def _init_cosmos(self):
        """Initialize Azure Cosmos DB connection."""
        from azure.cosmos import CosmosClient

        endpoint = os.getenv("COSMOS_ENDPOINT")
        key = os.getenv("COSMOS_KEY")

        if not endpoint or not key:
            raise ValueError("COSMOS_ENDPOINT or COSMOS_KEY not set")

        self.client = CosmosClient(endpoint, key)
        # Initialize specific container
        self.db_name = "bloom"
        self.container_name = "contributors"

    # ============ CONTRIBUTOR OPERATIONS ============

    def get_contributors(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all contributors for a guild."""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT uid, name, emoji_id FROM contributors WHERE guild_id = ?",
                (guild_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

        elif self.db_type == "cosmos":
            container = self.client.get_database_client(self.db_name).get_container_client(
                self.container_name
            )
            query = "SELECT * FROM c WHERE c.guild_id = @guild_id"
            items = list(container.query_items(query, parameters=[{"name": "@guild_id", "value": guild_id}]))
            return items

        else:
            # Azure SQL
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT uid, name, emoji_id FROM contributors WHERE guild_id = ?",
                guild_id,
            )
            return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    def add_contributor(self, guild_id: int, user_id: str, emoji: str, name: str = ""):
        """Add a contributor."""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO contributors (guild_id, uid, emoji_id, name) VALUES (?, ?, ?, ?)",
                (guild_id, user_id, emoji, name),
            )
            self.connection.commit()

        elif self.db_type == "cosmos":
            container = self.client.get_database_client(self.db_name).get_container_client(
                self.container_name
            )
            item = {
                "id": f"{guild_id}_{user_id}",
                "guild_id": guild_id,
                "uid": user_id,
                "emoji_id": emoji,
                "name": name,
            }
            container.create_item(item)

        else:
            # Azure SQL
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO contributors (guild_id, uid, emoji_id, name) VALUES (?, ?, ?, ?)",
                (guild_id, user_id, emoji, name),
            )
            self.connection.commit()

    def remove_contributor(self, guild_id: int, user_id: str):
        """Remove a contributor."""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM contributors WHERE guild_id = ? AND uid = ?",
                (guild_id, user_id),
            )
            self.connection.commit()

        elif self.db_type == "cosmos":
            container = self.client.get_database_client(self.db_name).get_container_client(
                self.container_name
            )
            container.delete_item(f"{guild_id}_{user_id}", partition_key=guild_id)

        else:
            # Azure SQL
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM contributors WHERE guild_id = ? AND uid = ?",
                (guild_id, user_id),
            )
            self.connection.commit()

    # ============ EVENTS OPERATIONS ============

    def get_events(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all events for a guild."""
        if self.db_type == "sqlite":
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM events WHERE guild_id = ?",
                (guild_id,),
            )
            return [dict(row) for row in cursor.fetchall()]
        # Similar implementation for other DB types...
        return []

    # ============ PROPOSALS OPERATIONS ============

    def create_proposal(self, guild_id: int, proposal_data: Dict[str, Any]):
        """Create a new proposal."""
        # Implementation depends on DB schema
        pass

    def get_proposals(self, guild_id: int) -> List[Dict[str, Any]]:
        """Get all proposals for a guild."""
        pass

    def close(self):
        """Close database connection."""
        if self.db_type in ["sqlite", "azure_sql"]:
            self.connection.close()
