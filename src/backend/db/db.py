"""Database helper for RenuevoChurch.

This module supports both SQLite and PostgreSQL connections. By default the
application still uses a local SQLite database file under `data/renuevo.db`.
When the `DATABASE_URL` environment variable is set or a DSN is passed to
`Database`, the app will use PostgreSQL instead.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple


try:
    import psycopg2
    import psycopg2.extras
except ImportError:  # pragma: no cover
    psycopg2 = None
    psycopg2_extras = None


DEFAULT_DB_DIR = Path(__file__).resolve().parents[3] / "data"
DEFAULT_DB_FILE = DEFAULT_DB_DIR / "renuevo.db"


class Database:
    """Database helper for SQLite and PostgreSQL.

    The helper exposes a small, consistent API used by repository code in the
    project. SQL parameter placeholders are translated automatically when a
    PostgreSQL connection is active.
    """

    def __init__(self, path: Optional[Path] = None, dsn: Optional[str] = None):
        if path and dsn:
            raise ValueError("Cannot specify both path and dsn")

        self.dsn = dsn
        if self.dsn is None:
            self.path = Path(path) if path else DEFAULT_DB_FILE
        else:
            self.path = None

        if self._is_sqlite:
            self._ensure_db_dir()

    @property
    def _is_sqlite(self) -> bool:
        return self.path is not None

    @property
    def backend(self) -> str:
        return "sqlite" if self._is_sqlite else "postgres"

    def _ensure_db_dir(self) -> None:
        """Create the parent directory for the DB file if it does not exist."""
        parent = self.path.parent
        parent.mkdir(parents=True, exist_ok=True)

    def _translate_sql(self, sql: str) -> str:
        if self._is_sqlite:
            return sql
        return sql.replace("?", "%s")

    @contextmanager
    def get_connection(self) -> Iterator[Any]:
        """Yield a configured database connection for the selected backend."""
        if self._is_sqlite:
            conn = sqlite3.connect(str(self.path))
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("PRAGMA foreign_keys = ON;")
                conn.execute("PRAGMA journal_mode = WAL;")
            except sqlite3.Error:
                pass

            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            if psycopg2 is None:
                raise RuntimeError("PostgreSQL support requires psycopg2-binary")

            conn = psycopg2.connect(self.dsn)
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()

    def execute(self, sql: str, params: Optional[Iterable[Any]] = None) -> None:
        """Execute a statement (use for CREATE/UPDATE/DELETE)."""
        sql = self._translate_sql(sql)
        with self.get_connection() as conn:
            if self._is_sqlite:
                if params is None:
                    conn.execute(sql)
                else:
                    conn.execute(sql, tuple(params))
            else:
                with conn.cursor() as cur:
                    cur.execute(sql, tuple(params) if params else ())

    def executemany(self, sql: str, seq_of_params: Iterable[Iterable[Any]]) -> None:
        """Execute the same statement for multiple rows of parameters."""
        sql = self._translate_sql(sql)
        with self.get_connection() as conn:
            if self._is_sqlite:
                conn.executemany(sql, tuple(tuple(row) for row in seq_of_params))
            else:
                with conn.cursor() as cur:
                    cur.executemany(sql, tuple(tuple(row) for row in seq_of_params))

    def query_all(self, sql: str, params: Optional[Iterable[Any]] = None) -> List[Any]:
        """Return all rows for the given query."""
        sql = self._translate_sql(sql)
        with self.get_connection() as conn:
            if self._is_sqlite:
                cur = conn.execute(sql, tuple(params) if params else ())
                return cur.fetchall()

            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, tuple(params) if params else ())
                return cur.fetchall()

    def query_one(self, sql: str, params: Optional[Iterable[Any]] = None) -> Optional[Any]:
        """Return a single row or None."""
        sql = self._translate_sql(sql)
        with self.get_connection() as conn:
            if self._is_sqlite:
                cur = conn.execute(sql, tuple(params) if params else ())
                return cur.fetchone()

            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, tuple(params) if params else ())
                return cur.fetchone()

    def insert(self, sql: str, params: Optional[Iterable[Any]] = None) -> int:
        """Run an INSERT and return the new row id."""
        sql = self._translate_sql(sql)
        with self.get_connection() as conn:
            if self._is_sqlite:
                cur = conn.execute(sql, tuple(params) if params else ())
                return cur.lastrowid

            upper_sql = sql.strip().upper()
            if upper_sql.startswith("INSERT") and "RETURNING" not in upper_sql:
                sql = sql.rstrip().rstrip(";") + " RETURNING *"

            with conn.cursor() as cur:
                cur.execute(sql, tuple(params) if params else ())
                row = cur.fetchone()
                return row[0] if row else -1

    def initialize_schema(self) -> None:
        """Create the database schema if it does not exist."""
        schema_statements = _get_schema_statements(self.backend)
        for stmt in schema_statements:
            self.execute(stmt)

        # Apply any pending migrations
        self._apply_migrations()

    def _apply_migrations(self) -> None:
        """Apply any pending database migrations."""
        if self._is_sqlite:
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
                pass

            try:
                with self.get_connection() as conn:
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
                pass

            return

        # PostgreSQL migrations
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'person'
                          AND column_name = 'ministry_id'
                        """
                    )
                    if cur.fetchone() is None:
                        cur.execute(
                            """
                            ALTER TABLE person
                            ADD COLUMN ministry_id INTEGER REFERENCES ministry(ministry_id) ON DELETE SET NULL
                            """
                        )

                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS person_ministry (
                            id SERIAL PRIMARY KEY,
                            person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
                            ministry_id INTEGER NOT NULL REFERENCES ministry(ministry_id) ON DELETE CASCADE,
                            area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
                            is_primary BOOLEAN DEFAULT FALSE
                        )
                        """
                    )
                    cur.execute(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS person_ministry_unique_idx
                        ON person_ministry (person_id, ministry_id, COALESCE(area_id, 0))
                        """
                    )
        except Exception:
            pass


def _get_schema_statements(backend: str) -> List[str]:
    """Return the CREATE TABLE statements for the application schema."""
    is_sqlite = backend == "sqlite"
    pk = "INTEGER PRIMARY KEY AUTOINCREMENT" if is_sqlite else "SERIAL PRIMARY KEY"
    boolean_default = "BOOLEAN DEFAULT 0" if is_sqlite else "BOOLEAN DEFAULT FALSE"

    return [
        # Consolidation levels
        f"""
        CREATE TABLE IF NOT EXISTS consolidation (
            consolidation_id {pk},
            level TEXT NOT NULL
        )
        """,

        # CDB (Casa de Bendición) houses
        f"""
        CREATE TABLE IF NOT EXISTS cdb (
            cdb_id {pk},
            number INTEGER NOT NULL UNIQUE
        )
        """,

        # Physical addresses
        f"""
        CREATE TABLE IF NOT EXISTS address (
            address_id {pk},
            street TEXT,
            neighborhood TEXT,
            house_number INTEGER
        )
        """,

        # Occupations (master table)
        f"""
        CREATE TABLE IF NOT EXISTS occupation (
            occupation_id {pk},
            name TEXT NOT NULL
        )
        """,

        # Ministry table
        f"""
        CREATE TABLE IF NOT EXISTS ministry (
            ministry_id {pk},
            name TEXT NOT NULL
        )
        """,

        # Ministry areas (each area belongs to a ministry, but ministries can have 0 areas)
        f"""
        CREATE TABLE IF NOT EXISTS ministry_area (
            area_id {pk},
            ministry_id INTEGER REFERENCES ministry(ministry_id) ON DELETE SET NULL,
            area TEXT NOT NULL
        )
        """,

        # Persons table (people)
        f"""
        CREATE TABLE IF NOT EXISTS person (
            person_id {pk},
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
            baptized {boolean_default},
            cdb INTEGER REFERENCES cdb(cdb_id) ON DELETE SET NULL,
            gender TEXT,
            membership_status TEXT
        )
        """,

        # Many-to-many between persons and ministries (optionally via areas)
        f"""
        CREATE TABLE IF NOT EXISTS person_ministry (
            {'id SERIAL PRIMARY KEY,' if not is_sqlite else ''}
            person_id INTEGER NOT NULL REFERENCES person(person_id) ON DELETE CASCADE,
            ministry_id INTEGER NOT NULL REFERENCES ministry(ministry_id) ON DELETE CASCADE,
            area_id INTEGER REFERENCES ministry_area(area_id) ON DELETE SET NULL,
            is_primary {boolean_default}
            {', PRIMARY KEY (person_id, ministry_id, area_id)' if is_sqlite else ''}
        )
        """,

        # Many-to-many between persons and occupations
        f"""
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
    if db._is_sqlite:
        print(f"Initializing database at: {db.path}")
    else:
        print("Initializing PostgreSQL schema")
    db.initialize_schema()
    print("Schema initialized.")

