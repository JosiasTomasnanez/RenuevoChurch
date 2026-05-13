"""Repository helpers for configuration-related queries (ministries, areas, consolidation, etc).

This module contains SQL query helpers for managing lookup tables:
- ministry (ministries)
- ministry_area (areas within a ministry)
- consolidation (consolidation levels)
- CDB-related configuration (stored as a simple table or enum-like setup)
"""
from typing import Dict, List, Optional

from ..db import db as _db_module

try:
    db = _db_module.db
except Exception:
    from ..db import db as db


# ============================================================================
# Ministry Management
# ============================================================================

def get_all_ministries() -> List[Dict]:
    """Return all ministries.
    
    Returns:
        List of dicts with ministry_id and name.
    """
    sql = "SELECT ministry_id, name FROM ministry ORDER BY name"
    rows = db.query_all(sql)
    return [{"ministry_id": r["ministry_id"], "name": r["name"]} for r in rows]


def get_ministry_by_id(ministry_id: int) -> Optional[Dict]:
    """Return a single ministry by id."""
    if ministry_id is None:
        return None
    sql = "SELECT ministry_id, name FROM ministry WHERE ministry_id = %s"
    row = db.query_one(sql, (ministry_id,))
    if row:
        return {"ministry_id": row["ministry_id"], "name": row["name"]}
    return None


def create_ministry(name: str) -> int:
    """Create a new ministry.
    
    Args:
        name: Ministry name.
    
    Returns:
        The id of the newly created ministry.
    """
    if not name:
        raise ValueError("Ministry name cannot be empty")
    sql = "INSERT INTO ministry (name) VALUES (%s)"
    return db.insert(sql, (name,))


def update_ministry(ministry_id: int, name: str) -> bool:
    """Update a ministry.
    
    Args:
        ministry_id: The id of the ministry to update.
        name: New ministry name.
    
    Returns:
        True if the update was successful.
    """
    if ministry_id is None or not name:
        return False
    sql = "UPDATE ministry SET name = %s WHERE ministry_id = %s"
    db.execute(sql, (name, ministry_id))
    return True


def delete_ministry(ministry_id: int) -> bool:
    """Delete a ministry (and cascade to its areas).
    
    Args:
        ministry_id: The id of the ministry to delete.
    
    Returns:
        True if the deletion was successful.
    """
    if ministry_id is None:
        return False
    # Areas will be deleted via CASCADE
    db.execute("DELETE FROM ministry WHERE ministry_id = %s", (ministry_id,))
    return True


# ============================================================================
# Ministry Area Management
# ============================================================================

def get_all_areas() -> List[Dict]:
    """Return all ministry areas with their ministry info."""
    sql = """
    SELECT ma.area_id, ma.ministry_id, ma.area, m.name AS ministry_name
    FROM ministry_area ma
    LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
    ORDER BY m.name, ma.area
    """
    rows = db.query_all(sql)
    return [
        {
            "area_id": r["area_id"],
            "ministry_id": r["ministry_id"],
            "area": r["area"],
            "ministry_name": r["ministry_name"]
        }
        for r in rows
    ]


def get_areas_by_ministry(ministry_id: int) -> List[Dict]:
    """Return all areas for a given ministry."""
    if ministry_id is None:
        return []
    sql = "SELECT area_id, ministry_id, area FROM ministry_area WHERE ministry_id = %s ORDER BY area"
    rows = db.query_all(sql, (ministry_id,))
    return [{"area_id": r["area_id"], "ministry_id": r["ministry_id"], "area": r["area"]} for r in rows]


def get_area_by_id(area_id: int) -> Optional[Dict]:
    """Return a single area by id."""
    if area_id is None:
        return None
    sql = "SELECT area_id, ministry_id, area FROM ministry_area WHERE area_id = %s"
    row = db.query_one(sql, (area_id,))
    if row:
        return {"area_id": row["area_id"], "ministry_id": row["ministry_id"], "area": row["area"]}
    return None


def create_area(ministry_id: int, area: str) -> int:
    """Create a new ministry area.
    
    Args:
        ministry_id: The ministry this area belongs to.
        area: The area name.
    
    Returns:
        The id of the newly created area.
    """
    if not area:
        raise ValueError("Area name cannot be empty")
    sql = "INSERT INTO ministry_area (ministry_id, area) VALUES (%s, %s)"
    return db.insert(sql, (ministry_id, area))


def update_area(area_id: int, area: str) -> bool:
    """Update a ministry area.
    
    Args:
        area_id: The id of the area to update.
        area: New area name.
    
    Returns:
        True if the update was successful.
    """
    if area_id is None or not area:
        return False
    sql = "UPDATE ministry_area SET area = %s WHERE area_id = %s"
    db.execute(sql, (area, area_id))
    return True


def delete_area(area_id: int) -> bool:
    """Delete a ministry area."""
    if area_id is None:
        return False
    db.execute("DELETE FROM ministry_area WHERE area_id = %s", (area_id,))
    return True


# ============================================================================
# Consolidation Level Management
# ============================================================================

def get_all_consolidations() -> List[Dict]:
    """Return all consolidation levels."""
    sql = "SELECT consolidation_id, level FROM consolidation ORDER BY level"
    rows = db.query_all(sql)
    return [{"consolidation_id": r["consolidation_id"], "level": r["level"]} for r in rows]


def get_consolidation_by_id(consolidation_id: int) -> Optional[Dict]:
    """Return a single consolidation level by id."""
    if consolidation_id is None:
        return None
    sql = "SELECT consolidation_id, level FROM consolidation WHERE consolidation_id = %s"
    row = db.query_one(sql, (consolidation_id,))
    if row:
        return {"consolidation_id": row["consolidation_id"], "level": row["level"]}
    return None


def create_consolidation(level: str) -> int:
    """Create a new consolidation level.
    
    Args:
        level: Consolidation level name.
    
    Returns:
        The id of the newly created consolidation level.
    """
    if not level:
        raise ValueError("Consolidation level cannot be empty")
    sql = "INSERT INTO consolidation (level) VALUES (%s)"
    return db.insert(sql, (level,))


def update_consolidation(consolidation_id: int, level: str) -> bool:
    """Update a consolidation level.
    
    Args:
        consolidation_id: The id of the consolidation to update.
        level: New level name.
    
    Returns:
        True if the update was successful.
    """
    if consolidation_id is None or not level:
        return False
    sql = "UPDATE consolidation SET level = %s WHERE consolidation_id = %s"
    db.execute(sql, (level, consolidation_id))
    return True


def delete_consolidation(consolidation_id: int) -> bool:
    """Delete a consolidation level."""
    if consolidation_id is None:
        return False
    db.execute("DELETE FROM consolidation WHERE consolidation_id = %s", (consolidation_id,))
    return True


# ============================================================================
# CDB (Casa de Bendición) Management
# ============================================================================

def get_all_cdb_options() -> List[Dict]:
    """Return all available CDB houses.
    
    Returns:
        List of dicts with cdb_id and number.
    """
    sql = "SELECT cdb_id, number FROM cdb ORDER BY number"
    rows = db.query_all(sql)
    return [{"cdb_id": r["cdb_id"], "number": r["number"]} for r in rows]


def get_cdb_by_id(cdb_id: int) -> Optional[Dict]:
    """Return a single CDB house by id."""
    if cdb_id is None:
        return None
    sql = "SELECT cdb_id, number FROM cdb WHERE cdb_id = %s"
    row = db.query_one(sql, (cdb_id,))
    if row:
        return {"cdb_id": row["cdb_id"], "number": row["number"]}
    return None


def create_cdb(number: int) -> int:
    """Create a new CDB house.
    
    Args:
        number: The house number.
    
    Returns:
        The id of the newly created CDB house.
    """
    if number is None:
        raise ValueError("CDB number cannot be empty")
    sql = "INSERT INTO cdb (number) VALUES (%s)"
    return db.insert(sql, (number,))


def update_cdb(cdb_id: int, number: int) -> bool:
    """Update a CDB house.
    
    Args:
        cdb_id: The id of the CDB to update.
        number: New house number.
    
    Returns:
        True if the update was successful.
    """
    if cdb_id is None or number is None:
        return False
    sql = "UPDATE cdb SET number = %s WHERE cdb_id = %s"
    db.execute(sql, (number, cdb_id))
    return True


def delete_cdb(cdb_id: int) -> bool:
    """Delete a CDB house."""
    if cdb_id is None:
        return False
    db.execute("DELETE FROM cdb WHERE cdb_id = %s", (cdb_id,))
    return True


__all__ = [
    "get_all_ministries",
    "get_ministry_by_id",
    "create_ministry",
    "update_ministry",
    "delete_ministry",
    "get_all_areas",
    "get_areas_by_ministry",
    "get_area_by_id",
    "create_area",
    "update_area",
    "delete_area",
    "get_all_consolidations",
    "get_consolidation_by_id",
    "create_consolidation",
    "update_consolidation",
    "delete_consolidation",
    "get_all_cdb_options",
    "get_cdb_by_id",
    "create_cdb",
    "update_cdb",
    "delete_cdb",
]
