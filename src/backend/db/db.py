"""Database helper for RenuevoChurch (SQLite)

This module provides a lightweight Database helper that manages a single
SQLite file located under the repository `data/` directory. It includes
helpers to execute queries and a schema initializer that will create the
tables needed by the application.

Tables created by the schema initializer:
- consolidation
- address
- occupation
- ministry_area
- person
- person_occupation (many-to-many)

The file path used is `data/renuevo.db` by default.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Iterator, List, Optional, Tuple


DEFAULT_DB_DIR = Path(__file__).resolve().parents[3] / "data"
DEFAULT_DB_FILE = DEFAULT_DB_DIR / "renuevo.db"


class Database:
    """Simple SQLite database helper.

    Use it as a context manager or call get_connection() to obtain a
    sqlite3.Connection. Provides convenience helpers for executing SQL and
    fetching results. All connections use sqlite3.Row as row_factory.
    """

    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else DEFAULT_DB_FILE
        self._ensure_db_dir()

    def _ensure_db_dir(self) -> None:
        """Create the parent directory for the DB file if it does not exist."""
        parent = self.path.parent
        parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def get_connection(self) -> Iterator[sqlite3.Connection]:
        """Yield an sqlite3.Connection configured with useful defaults.

        Connections use WAL journal mode and return rows as sqlite3.Row
        objects so callers can access columns by name.
        """
        conn = sqlite3.connect(str(self.path))
        conn.row_factory = sqlite3.Row
        # make database a bit friendlier for concurrent access
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
        except sqlite3.Error:
            # If something goes wrong, continue — PRAGMA errors are non-fatal
            pass

        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> None:
        """Execute a statement (use for CREATE/INSERT/UPDATE/DELETE).

        Example: db.execute("INSERT INTO table (a,b) VALUES (?,?)", (1,2))
        """
        with self.get_connection() as conn:
            if params is None:
                conn.execute(sql)
            else:
                conn.execute(sql, tuple(params))

    def executemany(self, sql: str, seq_of_params: Iterable[Iterable[Any]]) -> None:
        """Execute the same statement for multiple sets of parameters."""
        with self.get_connection() as conn:
            conn.executemany(sql, tuple(tuple(row) for row in seq_of_params))

    def query_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[sqlite3.Row]:
        """Return a list with all result rows for the query."""
        with self.get_connection() as conn:
            cur = conn.execute(sql, tuple(params) if params else ())
            return cur.fetchall()

    def query_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[sqlite3.Row]:
        """Return a single row or None."""
        with self.get_connection() as conn:
            cur = conn.execute(sql, tuple(params) if params else ())
            return cur.fetchone()

    def insert(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """Run an INSERT and return the last row id."""
        with self.get_connection() as conn:
            cur = conn.execute(sql, tuple(params) if params else ())
            return cur.lastrowid

    def initialize_schema(self) -> None:
        """Create the database schema if it does not exist.

        This will create all the tables required by the app using the English
        table and column names described in the project documentation.
        """
        schema_statements = _get_schema_statements()
        with self.get_connection() as conn:
            for stmt in schema_statements:
                conn.execute(stmt)
        
        # Apply any pending migrations
        self._apply_migrations()
    
    def _apply_migrations(self) -> None:
        """Apply any pending database migrations."""
        # Migration: Add ministry_id column to person table if it doesn't exist
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("PRAGMA table_info(person)")
                columns = {row[1] for row in cursor.fetchall()}

                if "ministry_id" not in columns:
                    conn.execute(
                        """
                        ALTER TABLE person
                        ADD COLUMN ministry_id INTEGER
                        REFERENCES ministry(ministry_id)
                        ON DELETE SET NULL
                        """
                    )
        except Exception:
            # Migration already applied or error — continue silently
            pass

        # Migration: Ensure person_ministry table exists and backfill data
        try:
            with self.get_connection() as conn:
                # Create table if it does not exist (for existing databases)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS person_ministry (
                        person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
                        ministry_id INTEGER NOT NULL REFERENCES ministry(ministry_id) ON DELETE CASCADE,
                        area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
                        is_primary BOOLEAN DEFAULT 0,
                        PRIMARY KEY (person_id, ministry_id, area_id)
                    )
                    """
                )

                # Backfill from person.ministry_area_id when present
                conn.execute(
                    """
                    INSERT INTO person_ministry (person_id, ministry_id, area_id, is_primary)
                    SELECT
                        p.person_id,
                        ma.ministry_id,
                        p.ministry_area_id,
                        1
                    FROM person p
                    JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
                    LEFT JOIN person_ministry pm
                        ON pm.person_id = p.person_id
                       AND pm.ministry_id = ma.ministry_id
                       AND (pm.area_id = p.ministry_area_id OR (pm.area_id IS NULL AND p.ministry_area_id IS NULL))
                    WHERE p.ministry_area_id IS NOT NULL
                      AND pm.person_id IS NULL
                    """
                )

                # Backfill from person.ministry_id when present and not already covered
                conn.execute(
                    """
                    INSERT INTO person_ministry (person_id, ministry_id, area_id, is_primary)
                    SELECT
                        p.person_id,
                        p.ministry_id,
                        NULL,
                        CASE
                            WHEN NOT EXISTS (
                                SELECT 1
                                FROM person_ministry pm2
                                WHERE pm2.person_id = p.person_id
                                  AND pm2.is_primary = 1
                            )
                            THEN 1
                            ELSE 0
                        END AS is_primary
                    FROM person p
                    LEFT JOIN person_ministry pm
                        ON pm.person_id = p.person_id
                       AND pm.ministry_id = p.ministry_id
                       AND pm.area_id IS NULL
                    WHERE p.ministry_id IS NOT NULL
                      AND pm.person_id IS NULL
                    """
                )
        except Exception:
            # If migration fails for any reason, continue without breaking startup
            pass


def _get_schema_statements() -> List[str]:
    """Return the CREATE TABLE statements for the application schema."""
    # The structure below matches the tables the project needs and uses
    # English names and columns mapped from the original Spanish design.
    return [
        # Consolidation levels
        """
        CREATE TABLE IF NOT EXISTS consolidation (
            consolidation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL
        )
        """,

        # CDB (Casa de Bendición) houses
        """
        CREATE TABLE IF NOT EXISTS cdb (
            cdb_id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER NOT NULL UNIQUE
        )
        """,

        # Physical addresses
        """
        CREATE TABLE IF NOT EXISTS address (
            address_id INTEGER PRIMARY KEY AUTOINCREMENT,
            street TEXT,
            neighborhood TEXT,
            house_number INTEGER
        )
        """,

        # Occupations (master table)
        """
        CREATE TABLE IF NOT EXISTS occupation (
            occupation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """,

        # Ministry table
        """
        CREATE TABLE IF NOT EXISTS ministry (
            ministry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """,

        # Ministry areas (each area belongs to a ministry, but ministries can have 0 areas)
        """
        CREATE TABLE IF NOT EXISTS ministry_area (
            area_id INTEGER PRIMARY KEY AUTOINCREMENT,
            ministry_id INTEGER REFERENCES ministry(ministry_id) ON DELETE SET NULL,
            area TEXT NOT NULL
        )
        """,

        # Persons table (people)
        """
        CREATE TABLE IF NOT EXISTS person (
            person_id INTEGER PRIMARY KEY AUTOINCREMENT,
            address_id INTEGER REFERENCES address(address_id) ON DELETE SET NULL,
            trusted_person_id INTEGER REFERENCES person(person_id) ON DELETE SET NULL,
            ministry_area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
            consolidation_id INTEGER REFERENCES consolidation(consolidation_id) ON DELETE SET NULL,
            future_ministry_area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            birthdate DATE,
            dni INTEGER,
            phone_number TEXT,
            marital_status TEXT,
            social_security TEXT,
            baptized BOOLEAN DEFAULT 0,
            cdb INTEGER REFERENCES cdb(cdb_id) ON DELETE SET NULL,
            gender TEXT,
            membership_status TEXT
        )
        """,

        # Many-to-many between persons and ministries (optionally via areas)
        """
        CREATE TABLE IF NOT EXISTS person_ministry (
            person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
            ministry_id INTEGER NOT NULL REFERENCES ministry(ministry_id) ON DELETE CASCADE,
            area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
            is_primary BOOLEAN DEFAULT 0,
            PRIMARY KEY (person_id, ministry_id, area_id)
        )
        """,

        # Many-to-many between persons and ministries (optionally via areas)
        """
        CREATE TABLE IF NOT EXISTS person_ministry (
            person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
            ministry_id INTEGER NOT NULL REFERENCES ministry(ministry_id) ON DELETE CASCADE,
            area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
            is_primary BOOLEAN DEFAULT 0,
            PRIMARY KEY (person_id, ministry_id, area_id)
        )
        """,

        # Many-to-many between persons and occupations
        """
        CREATE TABLE IF NOT EXISTS person_occupation (
            person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
            occupation_id INTEGER NOT NULL REFERENCES occupation(occupation_id) ON DELETE CASCADE,
            PRIMARY KEY (person_id, occupation_id)
        )
        """,
    ]


# Convenience top-level instance for simple scripts importing this module
db = Database()


if __name__ == "__main__":
    print(f"Initializing database at: {db.path}")
    db.initialize_schema()
    print("Schema initialized.")

