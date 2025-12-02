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
        SELECT p.*,
               a.address_id AS addr_address_id, a.street AS addr_street,
               a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
               ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
               m.ministry_id AS min_ministry_id, m.name AS min_name
        FROM person p
        LEFT JOIN address a ON p.address_id = a.address_id
        LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
        LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
        WHERE LOWER(a.neighborhood) LIKE LOWER(?)
        """
        params = (f"%{neighborhood}%",)
    else:
        sql = """
         SELECT p.*,
             a.address_id AS addr_address_id, a.street AS addr_street,
             a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
             ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
             m.ministry_id AS min_ministry_id, m.name AS min_name
         FROM person p
         LEFT JOIN address a ON p.address_id = a.address_id
         LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
         LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
         WHERE LOWER(a.neighborhood) = LOWER(?)
         """
        params = (neighborhood,)

    rows = db.query_all(sql, params)

    results = []
    for r in rows:
        row = dict(r)
        person_keys = {k: row[k] for k in row.keys() if not k.startswith("addr_") and not k.startswith("area_") and not k.startswith("min_")}
        address_keys = None
        if row.get("addr_address_id") is not None:
            address_keys = {
                "address_id": row.get("addr_address_id"),
                "street": row.get("addr_street"),
                "neighborhood": row.get("addr_neighborhood"),
                "house_number": row.get("addr_house_number"),
            }

        area_keys = None
        if row.get("area_area_id") is not None:
            area_keys = {
                "area_id": row.get("area_area_id"),
                "ministry_id": row.get("area_ministry_id"),
                "area": row.get("area_name"),
            }

        ministry_keys = None
        if row.get("min_ministry_id") is not None:
            ministry_keys = {
                "ministry_id": row.get("min_ministry_id"),
                "name": row.get("min_name"),
            }

        results.append({"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys})

    return results


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
    SELECT p.*,
           a.address_id AS addr_address_id, a.street AS addr_street,
           a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
           ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
           m.ministry_id AS min_ministry_id, m.name AS min_name
    FROM person p
    LEFT JOIN address a ON p.address_id = a.address_id
    LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
    LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
    WHERE ma.ministry_id = ?
    """

    rows = db.query_all(sql, (ministry_id,))

    results = []
    for r in rows:
        row = dict(r)
        person_keys = {k: row[k] for k in row.keys() if not k.startswith("addr_") and not k.startswith("area_") and not k.startswith("min_")}

        address_keys = None
        if row.get("addr_address_id") is not None:
            address_keys = {
                "address_id": row.get("addr_address_id"),
                "street": row.get("addr_street"),
                "neighborhood": row.get("addr_neighborhood"),
                "house_number": row.get("addr_house_number"),
            }

        area_keys = None
        if row.get("area_area_id") is not None:
            area_keys = {
                "area_id": row.get("area_area_id"),
                "ministry_id": row.get("area_ministry_id"),
                "area": row.get("area_name"),
            }

        ministry_keys = None
        if row.get("min_ministry_id") is not None:
            ministry_keys = {
                "ministry_id": row.get("min_ministry_id"),
                "name": row.get("min_name"),
            }

        results.append({"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys})

    return results


def find_people_by_name(name: str, partial: bool = True) -> List[Dict]:
    """Return people whose first or last name matches the provided value.

    By default this performs a "starts with" (prefix) match so searching for
    "Jo" will match "Jose" and "Jorge" but not "Benjo". If partial is
    False an exact equality match is performed.

    The function returns the same dict structure used by other helpers.
    """
    if not name:
        return []

    # partial==True => prefix match (name%)
    if partial:
        param = f"{name}%"
    else:
        param = name

    # Special-case handling for names that begin with 'ñ' (and uppercase 'Ñ').
    # Some SQLite builds do not perform Unicode-aware lowercasing correctly
    # for this character. When the search starts with 'ñ' we issue a query
    # that checks both the lower and upper-first variants using LIKE so
    # rows such as 'Ñañez' are matched correctly when the caller passes
    # 'ña' or 'ÑA'.
    if name and name[0].lower() == "ñ":
        capital = name[0].upper() + name[1:]
        # params: lower-prefix and capital-prefix, applied to first and last name
        params = (f"{param}", f"{capital}%", f"{param}", f"{capital}%")

        sql = """
        SELECT p.*,
               a.address_id AS addr_address_id, a.street AS addr_street,
               a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
               ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
               m.ministry_id AS min_ministry_id, m.name AS min_name
        FROM person p
        LEFT JOIN address a ON p.address_id = a.address_id
        LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
        LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
        WHERE p.first_name LIKE ? OR p.first_name LIKE ? OR p.last_name LIKE ? OR p.last_name LIKE ?
        """
    else:
        # default path: case-insensitive prefix match using LOWER
        if partial:
            params = (param, param)
        else:
            params = (name, name)

        sql = """
        SELECT p.*,
           a.address_id AS addr_address_id, a.street AS addr_street,
           a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
           ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
           m.ministry_id AS min_ministry_id, m.name AS min_name
    FROM person p
    LEFT JOIN address a ON p.address_id = a.address_id
    LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
    LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
        WHERE LOWER(p.first_name) LIKE LOWER(?) OR LOWER(p.last_name) LIKE LOWER(?)
    """

    # use the params tuple computed in the branches above
    rows = db.query_all(sql, params)

    results = []
    for r in rows:
        row = dict(r)
        person_keys = {k: row[k] for k in row.keys() if not k.startswith("addr_") and not k.startswith("area_") and not k.startswith("min_")}

        address_keys = None
        if row.get("addr_address_id") is not None:
            address_keys = {
                "address_id": row.get("addr_address_id"),
                "street": row.get("addr_street"),
                "neighborhood": row.get("addr_neighborhood"),
                "house_number": row.get("addr_house_number"),
            }

        area_keys = None
        if row.get("area_area_id") is not None:
            area_keys = {
                "area_id": row.get("area_area_id"),
                "ministry_id": row.get("area_ministry_id"),
                "area": row.get("area_name"),
            }

        ministry_keys = None
        if row.get("min_ministry_id") is not None:
            ministry_keys = {
                "ministry_id": row.get("min_ministry_id"),
                "name": row.get("min_name"),
            }

        results.append({"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys})

    return results


def find_all_people() -> List[Dict]:
    """Return all people rows, joined with address and area/ministry info.

    The result uses the same flattened/nested structure as the other
    helpers so callers can use Person.from_dict consistently.
    """
    sql = """
    SELECT p.*,
           a.address_id AS addr_address_id, a.street AS addr_street,
           a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number,
           ma.area_id AS area_area_id, ma.ministry_id AS area_ministry_id, ma.area AS area_name,
           m.ministry_id AS min_ministry_id, m.name AS min_name
    FROM person p
    LEFT JOIN address a ON p.address_id = a.address_id
    LEFT JOIN ministry_area ma ON p.ministry_area_id = ma.area_id
    LEFT JOIN ministry m ON ma.ministry_id = m.ministry_id
    """

    rows = db.query_all(sql)

    results = []
    for r in rows:
        row = dict(r)
        person_keys = {k: row[k] for k in row.keys() if not k.startswith("addr_") and not k.startswith("area_") and not k.startswith("min_")}

        address_keys = None
        if row.get("addr_address_id") is not None:
            address_keys = {
                "address_id": row.get("addr_address_id"),
                "street": row.get("addr_street"),
                "neighborhood": row.get("addr_neighborhood"),
                "house_number": row.get("addr_house_number"),
            }

        area_keys = None
        if row.get("area_area_id") is not None:
            area_keys = {
                "area_id": row.get("area_area_id"),
                "ministry_id": row.get("area_ministry_id"),
                "area": row.get("area_name"),
            }

        ministry_keys = None
        if row.get("min_ministry_id") is not None:
            ministry_keys = {
                "ministry_id": row.get("min_ministry_id"),
                "name": row.get("min_name"),
            }

        results.append({"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys})

    return results


__all__ = ["find_people_by_neighborhood", "find_people_by_ministry", "find_people_by_name"]
