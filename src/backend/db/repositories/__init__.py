"""Repository package exports.

Expose the repository helper functions with friendly names so other modules
can import them from `src.backend.db.repositories`.
"""
from .person_repository import (
    find_people_by_neighborhood as find_people_by_neighborhood,
    find_people_by_ministry as find_people_by_ministry,
)
from .ministry_repository import (
    get_area_and_ministry_by_area_id as get_area_and_ministry_by_area_id,
)

__all__ = [
    "find_people_by_neighborhood",
    "find_people_by_ministry",
    "get_area_and_ministry_by_area_id",
]
