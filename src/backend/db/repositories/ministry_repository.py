"""Repository helpers for ministry-related SQL queries.

The schema for this project contains `ministry_area` with fields
`area_id`, `ministry_id`, `area`. There isn't necessarily a `ministry`
table in the schema, so this helper first queries the area record, then
attempts to resolve a human-readable ministry name if such table exists.

The function returns a simple dictionary with the area id, area name,
ministry id and (optionally) ministry name.
"""
from typing import Dict, Optional
import sqlite3

from ..db import db as _db_module

try:
    db = _db_module.db
except Exception:  # pragma: no cover - defensive import fallback
    from ..db import db  # type: ignore


def get_area_and_ministry_by_area_id(area_id: int) -> Optional[Dict]:
    """Return area and ministry information for a given area_id.

    Returns a dictionary containing these keys when the area exists:
      - area_id: the numeric area id
      - area: area name (string)
      - ministry_id: numeric ministry id (may be null)
      - ministry_name: human-friendly ministry name when available, else None

    If the provided `area_id` does not match any row, returns None.
    """
    if area_id is None:
        return None

    # Get the area record first
    sql = "SELECT area_id, area, ministry_id FROM ministry_area WHERE area_id = ?"
    row = db.query_one(sql, (area_id,))
    if not row:
        return None

    result = {
        "area_id": row["area_id"],
        "area": row["area"],
        "ministry_id": row["ministry_id"],
        "ministry_name": None,
    }

    # Try to resolve the ministry name if a 'ministry' table exists. This
    # is defensive: missing table -> sqlite3.Error which we swallow.
    try:
        ministry_row = db.query_one("SELECT name FROM ministry WHERE ministry_id = ?", (row["ministry_id"],))
        if ministry_row:
            # sqlite3.Row works as a mapping
            result["ministry_name"] = ministry_row["name"]
    except sqlite3.Error:
        # Missing table or other sqlite error; leave ministry_name as None
        pass

    return result


__all__ = ["get_area_and_ministry_by_area_id"]
