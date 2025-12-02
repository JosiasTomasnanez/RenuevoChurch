"""Controller layer for person-related GUI actions.

This controller is intentionally lightweight and uses the app-provided
`services` module (attached by the backend app factory) and the `db` module
to perform operations. We avoid changing backend code — only use public
APIs exposed by `src.backend`.

Typical usage:
	# create app (backend/app.create_app) and then in GUI:
	from src.frontend.controllers import person_controller
	ctl = person_controller.get_controller(app.db, app.services)

The module exposes a small controller object with add/search/update helpers
that the Tkinter views can call.
"""
from __future__ import annotations

from typing import Optional, Dict, List
from dataclasses import dataclass
import logging

from src.backend.models.person import Person

logger = logging.getLogger(__name__)


@dataclass
class PersonController:
	db: object
	services: object

	def add_person(self, payload: Dict) -> int:
		"""Insert a person and optionally an address.

		Payload can include these keys (we only use a subset here):
		first_name, last_name, email, dni, phone_number,
		street, neighborhood, house_number

		Returns the created person_id.
		"""
		addr_id = None
		# Insert address if any address fields provided
		if any(payload.get(k) for k in ("street", "neighborhood", "house_number")):
			sql = "INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)"
			params = (payload.get("street"), payload.get("neighborhood"), payload.get("house_number"))
			addr_id = self.db.insert(sql, params)

		# Build person insert columns/values dynamically for safety
		cols = []
		vals = []
		if addr_id is not None:
			cols.append("address_id")
			vals.append(addr_id)

		for key in ("first_name", "last_name", "email", "dni", "phone_number"):
			if payload.get(key) is not None:
				cols.append(key)
				vals.append(payload.get(key))

		if not cols:
			raise ValueError("no person data provided")

		col_sql = ", ".join(cols)
		placeholder = ", ".join(["?"] * len(vals))
		sql = f"INSERT INTO person ({col_sql}) VALUES ({placeholder})"
		person_id = self.db.insert(sql, tuple(vals))
		logger.debug("Inserted person id=%s", person_id)
		return person_id

	def search(self, query: str, partial: bool = True) -> List[Dict]:
		"""Primary search by first name or last name (partial by default).

		This function intentionally only searches names — neighborhood-based
		searching was removed by request and will be implemented separately
		in the future if needed.
		"""
		# empty query -> return all people
		if not query:
			try:
				return self.services.people.get_all_people()
			except Exception:
				return []

		try:
			return self.services.people.get_people_by_name(query, partial=partial)
		except Exception:
			# if service isn't available for some reason, return an empty list
			return []

	def get_person(self, person_id: int) -> Optional[Person]:
		"""Fetch a single person by id — we query the person and address.

		Returns a Person model instance or None.
		"""
		if person_id is None:
			return None

		sql = "SELECT p.*, a.address_id AS addr_address_id, a.street AS addr_street, a.neighborhood AS addr_neighborhood, a.house_number AS addr_house_number FROM person p LEFT JOIN address a ON p.address_id = a.address_id WHERE p.person_id = ?"
		row = self.db.query_one(sql, (person_id,))
		if not row:
			return None
		# convert row to dict similar to repository shape
		r = dict(row)
		person_flat = {k: v for k, v in r.items() if not k.startswith("addr_")}
		address = None
		if r.get("addr_address_id") is not None:
			address = {
				"address_id": r.get("addr_address_id"),
				"street": r.get("addr_street"),
				"neighborhood": r.get("addr_neighborhood"),
				"house_number": r.get("addr_house_number"),
			}
		nested = {"person": person_flat, "address": address}
		return Person.from_dict(nested)

	def update_person(self, person_id: int, payload: Dict) -> bool:
		"""Update person and address fields (if present in payload).

		Returns True when update affected rows, False otherwise.
		"""
		if person_id is None:
			return False

		# Update address first if address fields provided
		address_fields = ("street", "neighborhood", "house_number")
		addr_vals = {k: payload[k] for k in address_fields if k in payload}
		if addr_vals:
			# fetch current address id
			cur = self.db.query_one("SELECT address_id FROM person WHERE person_id = ?", (person_id,))
			addr_id = None
			if cur:
				# sqlite3.Row may behave like a mapping but not implement get()
				try:
					addr_id = cur["address_id"]
				except Exception:
					try:
						addr_id = cur.get("address_id")
					except Exception:
						addr_id = None

			if addr_id:
				cols = ", ".join([f"{k} = ?" for k in addr_vals.keys()])
				params = tuple(addr_vals.values()) + (addr_id,)
				self.db.execute(f"UPDATE address SET {cols} WHERE address_id = ?", params)
			else:
				# No existing address — create one and attach to person
				sql = "INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)"
				params = (
					addr_vals.get("street"),
					addr_vals.get("neighborhood"),
					addr_vals.get("house_number"),
				)
				new_addr_id = self.db.insert(sql, params)
				# link new address to person
				self.db.execute("UPDATE person SET address_id = ? WHERE person_id = ?", (new_addr_id, person_id))

		# Update person simple fields
		person_fields = ("first_name", "last_name", "email", "dni", "phone_number")
		pvals = {k: payload[k] for k in person_fields if k in payload}
		if pvals:
			cols = ", ".join([f"{k} = ?" for k in pvals.keys()])
			params = tuple(pvals.values()) + (person_id,)
			self.db.execute(f"UPDATE person SET {cols} WHERE person_id = ?", params)

		return True


# module level singleton / helper
_ctrl: Optional[PersonController] = None


def get_controller(db: object, services: Optional[object] = None) -> PersonController:
	"""Return a cached controller instance for the GUI.

	The `services` value is optional because the backend `create_app` will
	attach a `services` variable into this module; callers can pass it
	explicitly as well.
	"""
	global _ctrl
	if _ctrl is None:
		from importlib import import_module

		# prefer explicitly passed services, fall back to module-level var
		module_services = services if services is not None else globals().get("services")
		if module_services is None:
			# try to import the services object from the backend app package
			# this is a last-resort and generally not needed when create_app is used
			try:
				app_main = import_module("src.backend.app.main")
				module_services = getattr(app_main, "services", None)
			except Exception:
				module_services = None

		# load the db module if needed
		_ctrl = PersonController(db=db, services=module_services)
	return _ctrl


__all__ = ["get_controller", "PersonController"]


