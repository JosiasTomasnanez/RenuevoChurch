"""Repository package exports.

Expose the repository helper functions with friendly names so other modules
can import them from `src.backend.db.repositories`.
"""
from .person_repository import (
    find_people_by_neighborhood as find_people_by_neighborhood,
    find_people_by_ministry as find_people_by_ministry,
    find_people_by_name as find_people_by_name,
    find_all_people as find_all_people,
    delete_person as delete_person,
)
from .ministry_repository import get_area_and_ministry

__all__ = [
    "find_people_by_neighborhood",
    "find_people_by_ministry",
    "find_all_people",
    "find_people_by_name",
    "delete_person",
    "get_area_and_ministry",
]
