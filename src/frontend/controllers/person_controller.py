"""Controller layer for person-related GUI actions.

This controller is a thin wrapper around the backend services layer.
It delegates all data operations to services and focuses only on:
- Accepting input from the GUI
- Calling appropriate service methods
- Returning results to the GUI

The module exposes a small controller object with methods that the
Tkinter views can call directly.

Typical usage:
	# create app (backend/app.create_app) and then in GUI:
	from src.frontend.controllers import person_controller
	ctl = person_controller.get_controller(app.services)
"""
from __future__ import annotations

from typing import Optional, Dict, List
from dataclasses import dataclass
import logging

from src.backend.models.person import Person

logger = logging.getLogger(__name__)


@dataclass
class PersonController:
	services: object

	def add_person(self, payload: Dict) -> int:
		"""Create a new person with optional address.

		Delegates to the services layer.

		Args:
			payload: Dictionary with person/address fields.

		Returns:
			The id of the newly created person.
		"""
		return self.services.people.create_person(payload)

	def search(self, query: str, partial: bool = True) -> List:
		"""Search people by first or last name.

		Returns empty list if query is empty or on error.

		Args:
			query: The name to search for.
			partial: If True, prefix matching; if False, exact match.

		Returns:
			List of Person objects matching the query.
		"""
		if not query:
			try:
				return self.services.people.get_all_people()
			except Exception:
				return []

		try:
			return self.services.people.get_people_by_name(query, partial=partial)
		except Exception:
			return []

	def get_person(self, person_id: int) -> Optional[Person]:
		"""Fetch a single person by id.

		Delegates to the services layer.

		Args:
			person_id: The id of the person to fetch.

		Returns:
			A Person object or None if not found.
		"""
		if person_id is None:
			return None

		try:
			return self.services.people.get_person(person_id)
		except Exception:
			logger.exception("Error fetching person %s", person_id)
			return None

	def update_person(self, person_id: int, payload: Dict) -> bool:
		"""Update person and/or address fields.

		Delegates to the services layer.

		Args:
			person_id: The id of the person to update.
			payload: Dictionary with fields to update.

		Returns:
			True if update succeeded, False otherwise.
		"""
		if person_id is None:
			return False

		try:
			return self.services.people.update_person(person_id, payload)
		except Exception:
			logger.exception("Error updating person %s", person_id)
			return False

	def delete_person(self, person_id: int) -> bool:
		"""Delete a person by id.

		Delegates to the services layer.

		Args:
			person_id: The id of the person to delete.

		Returns:
			True if deletion succeeded, False otherwise.
		"""
		if person_id is None:
			return False

		try:
			return self.services.people.delete_person(person_id)
		except Exception:
			logger.exception("Error deleting person %s", person_id)
			return False


# module level singleton / helper
_ctrl: Optional[PersonController] = None


def get_controller(services: Optional[object] = None) -> PersonController:
	"""Return a cached controller instance for the GUI.

	Args:
		services: The backend services object. If not provided, will try to use
				the module-level services variable set by the backend app factory.

	Returns:
		A PersonController instance.
	"""
	global _ctrl
	if _ctrl is None:
		from importlib import import_module

		# prefer explicitly passed services, fall back to module-level var
		module_services = services if services is not None else globals().get("services")
		if module_services is None:
			# try to import the services object from the backend app package
			try:
				app_main = import_module("src.backend.app.main")
				module_services = getattr(app_main, "services", None)
			except Exception:
				module_services = None

		if module_services is None:
			raise RuntimeError("services object is required to initialize PersonController")

		_ctrl = PersonController(services=module_services)
	return _ctrl


__all__ = ["get_controller", "PersonController"]


