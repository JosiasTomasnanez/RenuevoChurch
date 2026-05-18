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



def _normalize_value(value, to_int: bool = False):
    """Normalize empty strings to None and optionally cast to int."""
    if value == "":
        return None

    if to_int and value is not None:
        return int(value)

    return value

def _get_ministry_name(ministry_id: int) -> Optional[str]:
    """Helper to get ministry name by id."""
    if ministry_id is None:
        return None
    row = db.query_one("SELECT name FROM ministry WHERE ministry_id = %s", (ministry_id,))
    return row["name"] if row else None

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
        WHERE LOWER(a.neighborhood) LIKE LOWER(%s)
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
         WHERE LOWER(a.neighborhood) = LOWER(%s)
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
        elif row.get("area_ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("area_ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("area_ministry_id"),
                "name": ministry_name,
            }
        elif row.get("ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("ministry_id"),
                "name": ministry_name,
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
    WHERE ma.ministry_id = %s
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
        elif row.get("area_ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("area_ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("area_ministry_id"),
                "name": ministry_name,
            }
        elif row.get("ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("ministry_id"),
                "name": ministry_name,
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
        WHERE p.first_name LIKE %s OR p.first_name LIKE %s OR p.last_name LIKE %s OR p.last_name LIKE %s
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
        WHERE LOWER(p.first_name) LIKE LOWER(%s) OR LOWER(p.last_name) LIKE LOWER(%s)
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
        elif row.get("area_ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("area_ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("area_ministry_id"),
                "name": ministry_name,
            }
        elif row.get("ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("ministry_id"),
                "name": ministry_name,
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
        elif row.get("area_ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("area_ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("area_ministry_id"),
                "name": ministry_name,
            }
        elif row.get("ministry_id") is not None:
            ministry_name = _get_ministry_name(row.get("ministry_id"))
            ministry_keys = {
                "ministry_id": row.get("ministry_id"),
                "name": ministry_name,
            }

        results.append({"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys})

    return results


def delete_person(person_id: int) -> bool:
    """Delete a person row by id and, if the person had a private address
    that isn't referenced by any other person, remove that address as well.

    Returns True when a person row was deleted, False otherwise.
    """
    if person_id is None:
        return False

    # Fetch the person's address_id (if any) so we can conditionally
    # remove an orphaned address later.
    cur = db.query_one("SELECT address_id FROM person WHERE person_id = %s", (person_id,))
    addr_id = None
    if cur:
        try:
            addr_id = cur.get("address_id")
        except Exception:
            try:
                addr_id = cur["address_id"]
            except Exception:
                addr_id = None

    # Delete the person
    db.execute("DELETE FROM person WHERE person_id = %s", (person_id,))

    # If the deleted person had an address, ensure no other person still
    # references it — if not, delete the orphaned address row.
    if addr_id is not None:
        other = db.query_one("SELECT COUNT(1) AS cnt FROM person WHERE address_id = %s", (addr_id,))
        cnt = 0
        if other:
            try:
                cnt = int(other.get("cnt") or 0)
            except Exception:
                try:
                    cnt = int(other["cnt"] or 0)
                except Exception:
                    cnt = 0

        if cnt == 0:
            db.execute("DELETE FROM address WHERE address_id = %s", (addr_id,))

    return True


def find_person_by_id(person_id: int) -> Optional[Dict]:
    if person_id is None:
        return None

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
    WHERE p.person_id = %s""" # Eliminamos el salto de línea final antes de las comillas

    row = db.query_one(sql, (person_id,))
    if not row:
        return None

    r = dict(row)
    person_keys = {k: r[k] for k in r.keys() if not k.startswith("addr_") and not k.startswith("area_") and not k.startswith("min_")}

    address_keys = None
    if r.get("addr_address_id") is not None:
        address_keys = {
            "address_id": r.get("addr_address_id"),
            "street": r.get("addr_street"),
            "neighborhood": r.get("addr_neighborhood"),
            "house_number": r.get("addr_house_number"),
        }

    area_keys = None
    if r.get("area_area_id") is not None:
        area_keys = {
            "area_id": r.get("area_area_id"),
            "ministry_id": r.get("area_ministry_id"),
            "area": r.get("area_name"),
        }

    ministry_keys = None
    if r.get("min_ministry_id") is not None:
        ministry_keys = {
            "ministry_id": r.get("min_ministry_id"),
            "name": r.get("min_name"),
        }
    elif r.get("area_ministry_id") is not None:
        ministry_name = _get_ministry_name(r.get("area_ministry_id"))
        ministry_keys = {
            "ministry_id": r.get("area_ministry_id"),
            "name": ministry_name,
        }
    elif r.get("ministry_id") is not None:
        ministry_name = _get_ministry_name(r.get("ministry_id"))
        ministry_keys = {
            "ministry_id": r.get("ministry_id"),
            "name": ministry_name,
        }

    return {"person": person_keys, "address": address_keys, "area": area_keys, "ministry": ministry_keys}


def create_person(payload: Dict) -> int:
    """Insert a new person and optionally an address."""
    addr_id = None
    int_fields = {
        "house_number", "cdb", "ministry_id",
        "ministry_area_id", "consolidation_id", "future_ministry_area_id",
    }

    # --- Address ---
    address_fields = ("street", "neighborhood", "house_number")
    addr_vals = {}
    for key in address_fields:
        # CAMBIO: Si la clave está, la procesamos siempre
        if key in payload:
            value = _normalize_value(payload.get(key), to_int=(key in int_fields))
            if value is not None:
                addr_vals[key] = value

    if addr_vals:
        cols = ", ".join(addr_vals.keys())
        placeholders = ", ".join(["%s"] * len(addr_vals))
        sql = f"INSERT INTO address ({cols}) VALUES ({placeholders})"
        addr_id = db.insert(sql, tuple(addr_vals.values()))

    # --- Person ---
    cols = []
    vals = []

    if addr_id is not None:
        cols.append("address_id")
        vals.append(addr_id)

    person_fields = (
        "first_name", "last_name", "email", "birthdate", "gender",
        "dni", "phone_number", "marital_status", "social_security",
        "baptized", "cdb", "trusted_person_info", "ministry_id",
        "ministry_area_id", "consolidation_id", "future_ministry_area_id",
    )

    for key in person_fields:
        if key in payload:
            # Obtenemos el valor (puede ser None, "Masculino", etc.)
            value = _normalize_value(payload.get(key), to_int=(key in int_fields))
            
            # CAMBIO CRÍTICO: 
            # Agregamos la columna SIEMPRE que esté en el payload, 
            # permitiendo que guarde None (NULL en SQL) si el valor es vacío.
            cols.append(key)
            vals.append(value)

    if not cols:
        raise ValueError("no person data provided")

    col_sql = ", ".join(cols)
    placeholder_sql = ", ".join(["%s"] * len(vals))
    sql = f"INSERT INTO person ({col_sql}) VALUES ({placeholder_sql})"

    return db.insert(sql, tuple(vals))

def update_person(person_id: int, payload: Dict) -> bool:
    """Update person and/or address fields."""
    if person_id is None:
        return False

    int_fields = {
        "house_number",
        "cdb",
        "ministry_id",
        "ministry_area_id",
        "consolidation_id",
        "future_ministry_area_id",
    }

    # -----------------------------
    # Address
    # -----------------------------
    address_fields = ("street", "neighborhood", "house_number")

    addr_vals = {}

    for key in address_fields:
        if key not in payload:
            continue

        addr_vals[key] = _normalize_value(
            payload.get(key),
            to_int=(key in int_fields),
        )

    if addr_vals:
        cur = db.query_one(
            "SELECT address_id FROM person WHERE person_id = %s",
            (person_id,),
        )

        addr_id = None

        if cur:
            try:
                addr_id = cur["address_id"]
            except Exception:
                try:
                    addr_id = cur.get("address_id")
                except Exception:
                    addr_id = None

        if addr_id:
            cols = ", ".join([f"{k} = %s" for k in addr_vals.keys()])

            params = tuple(addr_vals.values()) + (addr_id,)

            db.execute(
                f"UPDATE address SET {cols} WHERE address_id = %s",
                params,
            )

        else:
            cols = ", ".join(addr_vals.keys())
            placeholders = ", ".join(["%s"] * len(addr_vals))

            sql = f"INSERT INTO address ({cols}) VALUES ({placeholders})"

            new_addr_id = db.insert(sql, tuple(addr_vals.values()))

            db.execute(
                "UPDATE person SET address_id = %s WHERE person_id = %s",
                (new_addr_id, person_id),
            )

    # -----------------------------
    # Person
    # -----------------------------
    person_fields = (
        "first_name",
        "last_name",
        "email",
        "birthdate",
        "gender",
        "dni",
        "phone_number",
        "marital_status",
        "social_security",
        "baptized",
        "cdb",
        "trusted_person_info",
        "ministry_id",
        "ministry_area_id",
        "consolidation_id",
        "future_ministry_area_id",
    )

    pvals = {}

    for key in person_fields:
        if key not in payload:
            continue

        pvals[key] = _normalize_value(
            payload.get(key),
            to_int=(key in int_fields),
        )

    if pvals:
        cols = ", ".join([f"{k} = %s" for k in pvals.keys()])

        params = tuple(pvals.values()) + (person_id,)

        db.execute(
            f"UPDATE person SET {cols} WHERE person_id = %s",
            params,
        )

    return True

__all__ = [
    "find_people_by_neighborhood",
    "find_people_by_ministry",
    "find_people_by_name",
    "find_all_people",
    "delete_person",
    "find_person_by_id",
    "create_person",
    "update_person",
]
