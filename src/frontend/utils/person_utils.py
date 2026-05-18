"""
Utilities for handling person data transformations.

Este módulo se encarga de:
- Normalizar estructuras de persona (dict / objeto)
- Extraer campos comunes
- Resolver relaciones (cdb, ministry, address)
"""

# ---------------------------
# Basic extractors
# ---------------------------

def get_person_id(p):
    if isinstance(p, dict):
        person = p.get("person") if "person" in p else p
        return person.get("person_id")
    return getattr(p, "person_id", None)


def get_person_field(p, field):
    """Generic safe getter for flat or nested dict/object."""
    if isinstance(p, dict):
        if field in p:
            return p.get(field)

        # nested address
        addr = p.get("address")
        if isinstance(addr, dict) and field in addr:
            return addr.get(field)

        # nested person
        if "person" in p:
            return p["person"].get(field)

        return None

    # object
    if hasattr(p, field):
        return getattr(p, field)

    if hasattr(p, "address") and hasattr(p.address, field):
        return getattr(p.address, field)

    return None


# ---------------------------
# Baptized
# ---------------------------

def is_baptized(p):
    val = get_person_field(p, "baptized")
    return bool(val)


# ---------------------------
# CDB
# ---------------------------

def get_person_cdb_id(p):
    return get_person_field(p, "cdb")


def resolve_cdb_number(p, config_service=None):
    """
    Convierte cdb_id -> número real (ej: casa 12)
    """
    cdb_id = get_person_cdb_id(p)

    if not cdb_id:
        return None

    if config_service:
        try:
            cdb = config_service.get_cdb_by_id(cdb_id)
            if cdb:
                return cdb.get("number")
        except Exception:
            pass

    return cdb_id  # fallback



# ---------------------------
# Address helpers
# ---------------------------

def get_full_address(p):
    street = get_person_field(p, "street")
    number = get_person_field(p, "house_number")
    neighborhood = get_person_field(p, "neighborhood")

    parts = []

    if street:
        if number:
            parts.append(f"{street} {number}")
        else:
            parts.append(street)

    if neighborhood:
        parts.append(neighborhood)

    return ", ".join(parts) if parts else None


# ---------------------------
# Normalization
# ---------------------------

def normalize_person(p, config_service=None):
    """
    Devuelve un dict limpio y consistente
    para usar en UI o API responses.
    """

    return {
        "person_id": get_person_id(p),
        "first_name": get_person_field(p, "first_name"),
        "last_name": get_person_field(p, "last_name"),
        "dni": get_person_field(p, "dni"),
        "phone_number": get_person_field(p, "phone_number"),
        "baptized": is_baptized(p),
        "cdb_number": resolve_cdb_number(p, config_service),
        "address": get_full_address(p),
    }
