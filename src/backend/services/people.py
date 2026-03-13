"""Service layer for person-related operations.

This small service wraps the repository helpers and maps database rows into
typed `Person` objects from `src.backend.models.person`.
"""
from typing import List, Optional

from ..db.repositories import (
	find_people_by_neighborhood,
	find_people_by_ministry,
	find_people_by_name,
	find_person_by_id,
	create_person as _repo_create,
	update_person as _repo_update,
	list_memberships_by_person,
	find_person_ids_by_ministry,
	set_memberships_for_person,
)
from ..models.person import Person
from ..db.repositories import get_area_and_ministry


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


def get_memberships_for_person(person_id: int):
	"""Return raw membership dicts for a given person_id."""
	return list_memberships_by_person(person_id)


__all__.append("get_memberships_for_person")


def delete_person(person_id: int) -> bool:
	"""Delete a person by id using repository helpers.

	Returns True when deletion succeeded (person removed), False otherwise.
	"""
	try:
		from ..db.repositories import delete_person as _repo_delete

		return bool(_repo_delete(person_id))
	except Exception:
		return False


__all__.append("delete_person")


def create_person(payload: dict) -> int:
	"""Create a new person with optional address.

	Args:
		payload: Dictionary with person/address fields (first_name, last_name, email, dni,
				phone_number, street, neighborhood, house_number).

	Returns:
		The id of the newly created person.
	"""
	return _repo_create(payload)


__all__.append("create_person")


def get_person(person_id: int) -> Optional[Person]:
	"""Fetch a single person by id.

	Returns:
		A Person object or None if not found.
	"""
	if person_id is None:
		return None

	row = find_person_by_id(person_id)
	if row is None:
		return None

	return Person.from_dict(row)


__all__.append("get_person")


def update_person(person_id: int, payload: dict) -> bool:
	"""Update person and/or address fields.

	Args:
		person_id: The id of the person to update.
		payload: Dictionary with fields to update.

	Returns:
		True if update succeeded, False otherwise.
	"""
	return _repo_update(person_id, payload)


__all__.append("update_person")


def update_person_memberships(person_id: int, memberships: list) -> None:
	"""Update the many-to-many memberships for a person.

	`memberships` is a list of dicts with at least `ministry_id` and
	optionally `area_id`. The `is_primary` flag is optional and not
	required by the UI (all can be treated as no principal).
	"""
	set_memberships_for_person(person_id, memberships)


__all__.append("update_person_memberships")

