"""Service layer for person-related operations.

This small service wraps the repository helpers and maps database rows into
typed `Person` objects from `src.backend.models.person`.
"""
from typing import List, Optional
import logging
import re
from datetime import datetime

from ..db.repositories import (
    find_people_by_neighborhood,
    find_people_by_name,
    find_person_by_id,
    create_person as _repo_create,
    update_person as _repo_update,
    list_memberships_by_person,
    find_person_ids_by_ministry,
    set_memberships_for_person,
    # NUEVOS IMPORTS DESDE EL REPOSITORIO DE PERSONA
    get_person_occupations,
    update_person_occupations,
    find_people_by_occupation,
)
from ..models.person import Person
from ..db.repositories import get_area_and_ministry

logger = logging.getLogger(__name__)


def get_people_by_neighborhood(neighborhood: str, partial: bool = False) -> List[Person]:
    """Return Person objects for people living in the given neighborhood."""
    rows = find_people_by_neighborhood(neighborhood, partial=partial)
    return [Person.from_dict(r) for r in rows]


def get_people_by_ministry(ministry_id: int) -> List[Person]:
    """Return Person objects for people that belong to the given ministry id.

    This implementation uses the person_ministry join table to support
    multiple memberships per person. For now it returns one Person per
    person_id; membership details can be obtained via
    `get_memberships_for_person`.
    """
    person_ids = find_person_ids_by_ministry(ministry_id)
    people: List[Person] = []
    for pid in person_ids:
        p = get_person(pid)
        if p is not None:
            people.append(p)
    return people


__all__ = ["get_people_by_neighborhood", "get_people_by_ministry"]


def get_people_by_name(name: str, partial: bool = True) -> List[Person]:
    """Return Person objects that match first name or last name.

    Partial matching is enabled by default so searching for 'An' will match
    'Ana' and 'Andrew'.
    """
    q = (name or "")
    q = q.strip()
    q_for_repo = q

    rows = find_people_by_name(q_for_repo, partial=partial)
    people = [Person.from_dict(r) for r in rows]

    q = (name or "")
    if not q:
        return people

    q_fold = q.casefold()

    def matches(p: Person) -> bool:
        for field in (p.first_name, p.last_name):
            if field is None:
                continue
            f = str(field).casefold()
            if partial:
                if f.startswith(q_fold):
                    return True
            else:
                if f == q_fold:
                    return True
        return False

    return [p for p in people if matches(p)]


__all__.append("get_people_by_name")


def get_all_people() -> List[Person]:
    """Return all people from the database as Person objects."""
    try:
        from ..db.repositories import find_all_people
        rows = find_all_people()
    except Exception:
        return []

    return [Person.from_dict(r) for r in rows]


__all__.append("get_all_people")

def get_area_and_ministry_service(area_id: int):
    """Small convenience service wrapper around the repository helper."""
    return get_area_and_ministry(area_id)


__all__.append("get_area_and_ministry_service")


def get_memberships_for_person(person_id: int):
    """Return raw membership dicts for a given person_id."""
    return list_memberships_by_person(person_id)


__all__.append("get_memberships_for_person")


def delete_person(person_id: int) -> bool:
    """Delete a person by id using repository helpers."""
    try:
        from ..db.repositories import delete_person as _repo_delete
        return bool(_repo_delete(person_id))
    except Exception:
        return False


__all__.append("delete_person")


def create_person(payload: dict) -> int:
    """Create a new person with optional address and handles multiple occupations.

    Args:
        payload: Dictionary with fields. May include 'occupation_ids' (List[int]).
    """
    _validate_person_payload(payload)
    
    # Extraemos las ocupaciones del payload para que no molesten al repositorio base de person
    occupation_ids = payload.pop("occupation_ids", [])
    
    # Creamos la persona
    person_id = _repo_create(payload)
    
    # Si todo salió bien y tenemos ocupaciones (o para limpiar si viniera vacío), guardamos en la tabla intermedia
    if person_id and isinstance(occupation_ids, list):
        update_person_occupations(person_id, occupation_ids)
        
    return person_id


__all__.append("create_person")


def get_person(person_id: int) -> Optional[Person]:
    """Fetch a single person by id, injecting their assigned occupations."""
    if person_id is None:
        return None

    row = find_person_by_id(person_id)
    if row is None:
        return None

    # Creamos la instancia del modelo Person
    person_obj = Person.from_dict(row)
    
    # NUEVO: Traemos las ocupaciones y se las inyectamos dinámicamente si tu modelo lo requiere,
    # o las dejamos disponibles como atributo de la instancia (ej. person_obj.occupations)
    if person_obj:
        person_obj.occupations = get_person_occupations(person_id)

    return person_obj


__all__.append("get_person")


def update_person(person_id: int, payload: dict) -> bool:
    """Update person, address and their many-to-many occupations."""
    _validate_person_payload(payload)
    
    # Extraemos las ocupaciones si vienen en el payload para manejarlas por separado
    has_occupations = "occupation_ids" in payload
    occupation_ids = payload.pop("occupation_ids", [])
    
    success = _repo_update(person_id, payload)
    
    # Sincronizamos las ocupaciones si el campo fue enviado desde la vista
    if success and has_occupations:
        update_person_occupations(person_id, occupation_ids)
        
    return success


__all__.append("update_person")


def update_person_memberships(person_id: int, memberships: list) -> None:
    """Update the many-to-many memberships for a person."""
    logger.info(f"Updating memberships for person {person_id}: {memberships}")
    set_memberships_for_person(person_id, memberships)


__all__.append("update_person_memberships")


# =========================================================================
# NUEVOS MÉTODOS DE SERVICIO PARA OCUPACIONES
# =========================================================================

def get_occupations_by_person(person_id: int) -> List[dict]:
    """Retorna las ocupaciones asignadas a una persona como lista de dicts."""
    return get_person_occupations(person_id)


def get_people_by_occupation(occupation_id: int) -> List[Person]:
    """Retorna los objetos Person que pertenecen a una ocupación específica."""
    rows = find_people_by_occupation(occupation_id)
    return [Person.from_dict(r) for r in rows]


__all__.extend(["get_occupations_by_person", "get_people_by_occupation"])


def _validate_person_payload(payload: dict):
    """Valida y normaliza la coherencia de los datos. Lanza ValueError si falla."""
    text_fields = ["first_name", "last_name", "neighborhood", "street", "email", "trusted_person_info"]
    
    for field in text_fields:
        val = payload.get(field)
        if isinstance(val, str):
            val = val.strip()
            val = re.sub(r'\s+', ' ', val)
            
            if field == "email":
                payload[field] = val.lower()
            else:
                payload[field] = val.title()
    
    email = payload.get("email")
    if email:
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            raise ValueError(f"El formato del correo '{email}' no es válido.")
        
    gender = payload.get("gender")
    if gender:
        normalized_gender = str(gender).strip().title()
        valid_genders = ["Masculino", "Femenino"]
        
        if normalized_gender not in valid_genders:
            raise ValueError(f"Género '{gender}' no válido. Opciones: {', '.join(valid_genders)}.")
        
        payload["gender"] = normalized_gender

    birthdate = payload.get("birthdate")
    if birthdate:
        try:
            if isinstance(birthdate, str):
                b_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
            else:
                b_date = birthdate.date() if hasattr(birthdate, "date") else birthdate 
            
            if b_date > datetime.now().date():
                raise ValueError("La fecha de nacimiento no puede ser posterior al día de hoy.")
            if b_date.year < 1900:
                raise ValueError("La fecha de nacimiento no es válida (año demasiado antiguo).")
                
            payload["birthdate"] = b_date
            
        except ValueError as e:
            if "format" in str(e):
                raise ValueError("El formato de fecha debe ser YYYY-MM-DD.")
            raise e

    if not payload.get("first_name") or not payload.get("last_name"):
        raise ValueError("El nombre y el apellido son obligatorios.")

    return payload