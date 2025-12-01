"""Repository helpers for person-related SQL queries.

This module contains straightforward SQL query helpers that talk directly to
the application's lightweight SQLite wrapper (`db`) so that services/controllers
don't need to build ad-hoc SQL statements.

Functions provided:
- find_people_by_neighborhood(neighborhood, partial=False)
- find_people_by_ministry(ministry_id)

These return lists of dictionaries (one dict per person row), including a
small set of address/ministry fields joined for convenience.
"""
from typing import Dict, List, Optional

from ..db import db as _db_module

# Import the database instance exported by ../db.py
try:
    db = _db_module.db
except Exception:  # pragma: no cover - defensive: keep module import stable
    # fall back in case the name resolution changes; keep it explicit
    from ..db import db as db


def find_people_by_neighborhood(neighborhood: str, partial: bool = False) -> List[Dict]:
    """Return people living in a given neighborhood.

    Args:
        neighborhood: Neighborhood name to match (case-insensitive).
        partial: If True, does a substring match (LIKE %%<neighborhood>%%).

    Returns:
        A list of dictionaries, each representing a person row joined with
        a few address fields for convenience. Empty list if no matches.
    """
    if not neighborhood:
        return []

    if partial:
        sql = """
        SELECT p.*, a.street AS street, a.neighborhood AS neighborhood,
               a.house_number AS house_number
        FROM person p
        LEFT JOIN address a ON p.address_id = a.address_id
        WHERE LOWER(a.neighborhood) LIKE LOWER(?)
        """
        params = (f"%{neighborhood}%",)
    else:
        sql = """
        SELECT p.*, a.street AS street, a.neighborhood AS neighborhood,
               a.house_number AS house_number
        FROM person p
        LEFT JOIN address a ON p.address_id = a.address_id
        WHERE LOWER(a.neighborhood) = LOWER(?)
        """
        params = (neighborhood,)

    rows = db.query_all(sql, params)
    return [dict(r) for r in rows]


def find_people_by_ministry(ministry_id: int) -> List[Dict]:
    """Return people that belong to a given ministry.

    Note: the application schema stores a person's current ministry area via
    `person.ministry_area_id` which references `ministry_area(area_id)`.
    The `ministry_area` table contains `ministry_id` which we use to filter.

    Args:
        ministry_id: Integer id of the ministry to filter by.

    Returns:
        List of dictionaries for each matching person row, including the
        person's ministry area name and ministry id.
    """
    if ministry_id is None:
        return []

    sql = """
    SELECT p.*, ma.area AS ministry_area, ma.ministry_id
    FROM person p
    LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
    WHERE ma.ministry_id = ?
    """

    rows = db.query_all(sql, (ministry_id,))
    return [dict(r) for r in rows]


__all__ = ["find_people_by_neighborhood", "find_people_by_ministry"]
