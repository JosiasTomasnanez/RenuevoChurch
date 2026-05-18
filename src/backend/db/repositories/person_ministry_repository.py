"""Repository helpers for person-ministry memberships.

This module centralizes all access to the `person_ministry` join table, which
models the many-to-many relationship between people and ministries (optionally
via areas).
"""
from typing import Dict, Iterable, List, Optional
import logging

from ..db import db as _db_module

logger = logging.getLogger(__name__)

try:
    db = _db_module.db
except Exception:  # pragma: no cover - defensive: keep module import stable
    from ..db import db as db


def list_memberships_by_person(person_id: int) -> List[Dict]:
    """Return all ministry memberships for a given person.

    Each result row includes joined ministry and area information:
        {
            "person_id": ...,
            "ministry_id": ...,
            "area_id": ...,
            "is_primary": 0/1,
            "ministry": {"ministry_id": ..., "name": ...} or None,
            "area": {"area_id": ..., "ministry_id": ..., "area": ...} or None,
        }
    """
    if person_id is None:
        return []

    sql = """
    SELECT
        pm.person_id,
        pm.ministry_id,
        pm.area_id,
        pm.is_primary,
        m.ministry_id AS m_id,
        m.name AS m_name,
        ma.area_id AS a_id,
        ma.ministry_id AS a_ministry_id,
        ma.area AS a_name
    FROM person_ministry pm
    LEFT JOIN ministry m ON pm.ministry_id = m.ministry_id
    LEFT JOIN ministry_area ma ON pm.area_id = ma.area_id
    WHERE pm.person_id = %s
    ORDER BY pm.is_primary DESC, m.name, ma.area
    """
    rows = db.query_all(sql, (person_id,))

    result: List[Dict] = []
    for r in rows:
        row = dict(r)
        ministry: Optional[Dict] = None
        if row.get("m_id") is not None:
            ministry = {"ministry_id": row.get("m_id"), "name": row.get("m_name")}

        area: Optional[Dict] = None
        if row.get("a_id") is not None:
            area = {
                "area_id": row.get("a_id"),
                "ministry_id": row.get("a_ministry_id"),
                "area": row.get("a_name"),
            }

        result.append(
            {
                "person_id": row.get("person_id"),
                "ministry_id": row.get("ministry_id"),
                "area_id": row.get("area_id"),
                "is_primary": row.get("is_primary", 0),
                "ministry": ministry,
                "area": area,
            }
        )

    return result


def set_memberships_for_person(person_id: int, memberships: Iterable[Dict]) -> None:
    """Replace all memberships for a person with the provided set."""
    if person_id is None:
        return

    logger.info(f"Setting memberships for person {person_id}: {list(memberships)}")

    # Normalize input and enforce single primary flag
    normalized: List[Dict] = []
    any_primary = False
    for m in memberships:
        if not m:
            continue
        ministry_id = m.get("ministry_id")
        if ministry_id is None:
            continue
        
        area_id = m.get("area_id")
        # Cambiamos a bool real de Python
        is_primary = bool(m.get("is_primary", False))
        
        if is_primary and not any_primary:
            any_primary = True
        else:
            if any_primary:
                is_primary = False
        
        normalized.append(
            {
                "ministry_id": ministry_id,
                "area_id": area_id,
                "is_primary": is_primary, # Guardamos True/False
            }
        )

    # Si ninguno es primario, marcamos el primero como True
    if normalized and not any_primary:
        normalized[0]["is_primary"] = True

    logger.info(f"Normalized memberships: {normalized}")

    # Eliminar existentes
    db.execute("DELETE FROM person_ministry WHERE person_id = %s", (person_id,))

    if not normalized:
        return

    sql = """
    INSERT INTO person_ministry (person_id, ministry_id, area_id, is_primary)
    VALUES (%s, %s, %s, %s)
    """
    
    # Aquí es donde ocurre la magia: al pasar True/False, psycopg2 lo traduce a BOOLEAN de Postgres
    params = [
        (person_id, m["ministry_id"], m.get("area_id"), m["is_primary"])
        for m in normalized
    ]
    
    logger.info(f"Inserting params: {params}")
    db.executemany(sql, params)

def find_person_ids_by_ministry(ministry_id: int) -> List[int]:
    """Return distinct person_ids that are members of the given ministry."""
    if ministry_id is None:
        return []

    sql = """
    SELECT DISTINCT person_id
    FROM person_ministry
    WHERE ministry_id = %s
    """
    rows = db.query_all(sql, (ministry_id,))
    return [int(r["person_id"]) for r in rows if r["person_id"] is not None]


__all__ = [
    "list_memberships_by_person",
    "set_memberships_for_person",
    "find_person_ids_by_ministry",
]

