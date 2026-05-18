"""Repository helpers for ministry lookups.

Provides a small helper to get the ministry area and ministry name for a
given area_id. Returns a dict with `area` and `ministry` keys (or None values
if not found) so services can construct model objects.
"""
from typing import Dict, Optional

from ..db import db as _db_module

try:
    db = _db_module.db
except Exception:  # pragma: no cover - defensive
    from ..db import db as db  # type: ignore


def get_area_and_ministry(area_id: int) -> Optional[Dict]:
    """Return a dict with 'area' and 'ministry' for the given area_id.

    Example return value:
        {"area": {"area_id": 1, "area": "Worship", "ministry_id": 2},
         "ministry": {"ministry_id": 2, "name": "Music"}}

    Returns None if no area found.
    """
    if area_id is None:
        return None

    sql = """
    SELECT ma.area_id AS area_id, ma.area AS area_name, ma.ministry_id AS ministry_id,
           m.ministry_id AS min_id, m.name AS ministry_name
    FROM ministry_area ma
    LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
    WHERE ma.area_id = %s
    """

    row = db.query_one(sql, (area_id,))
    if not row:
        return None

    r = dict(row)
    area = {"area_id": r.get("area_id"), "area": r.get("area_name"), "ministry_id": r.get("ministry_id")}
    ministry = None
    if r.get("min_id") is not None:
        ministry = {"ministry_id": r.get("min_id"), "name": r.get("ministry_name")}

    return {"area": area, "ministry": ministry}


__all__ = ["get_area_and_ministry"]

