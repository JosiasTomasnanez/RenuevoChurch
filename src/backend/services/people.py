"""Service layer for person-related operations.

This small service wraps the repository helpers and maps database rows into
typed `Person` objects from `src.backend.models.person`.
"""
from typing import List

from ..db.repositories import find_people_by_neighborhood, find_people_by_ministry
from ..models.person import Person
from ..db.repositories import get_area_and_ministry


def get_people_by_neighborhood(neighborhood: str, partial: bool = False) -> List[Person]:
	"""Return Person objects for people living in the given neighborhood."""
	rows = find_people_by_neighborhood(neighborhood, partial=partial)
	return [Person.from_dict(r) for r in rows]


def get_people_by_ministry(ministry_id: int) -> List[Person]:
	"""Return Person objects for people that belong to the given ministry id."""
	rows = find_people_by_ministry(ministry_id)
	return [Person.from_dict(r) for r in rows]


__all__ = ["get_people_by_neighborhood", "get_people_by_ministry"]

def get_area_and_ministry_service(area_id: int):
	"""Small convenience service wrapper around the repository helper.

	Returns the same dict structure produced by the repository or None.
	"""
	return get_area_and_ministry(area_id)


__all__.append("get_area_and_ministry_service")

