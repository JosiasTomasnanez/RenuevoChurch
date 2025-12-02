"""Service layer for person-related operations.

This small service wraps the repository helpers and maps database rows into
typed `Person` objects from `src.backend.models.person`.
"""
from typing import List

from ..db.repositories import find_people_by_neighborhood, find_people_by_ministry, find_people_by_name
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


def get_people_by_name(name: str, partial: bool = True) -> List[Person]:
	"""Return Person objects that match first name or last name.

	Partial matching is enabled by default so searching for 'An' will match
	'Ana' and 'Andrew'.
	"""
	# Normalize query before calling the repository: trim whitespace.
	# We intentionally do NOT force lowercasing here so callers that include
	# special characters (like 'Ñ') keep their original form and the
	# repository can handle special-case matching for such characters.
	q = (name or "")
	q = q.strip()
	q_for_repo = q

	rows = find_people_by_name(q_for_repo, partial=partial)
	people = [Person.from_dict(r) for r in rows]

	# Perform a Unicode-aware casefold prefix/equality check on the
	# service layer so searches match characters like 'ñ' vs 'Ñ'. SQLite's
	# built-in case-insensitive matching is ASCII-only on many builds, so
	# we enforce the requested semantics here.
	q = (name or "")
	if not q:
		return people

	q_fold = q.casefold()

	def matches(p: Person) -> bool:
		# match against first_name or last_name
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
		# If the repository helper isn't available, return empty list
		return []

	return [Person.from_dict(r) for r in rows]


__all__.append("get_all_people")

def get_area_and_ministry_service(area_id: int):
	"""Small convenience service wrapper around the repository helper.

	Returns the same dict structure produced by the repository or None.
	"""
	return get_area_and_ministry(area_id)


__all__.append("get_area_and_ministry_service")

