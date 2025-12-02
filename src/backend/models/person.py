"""Tiny models used by the People service and tests.

These models are intentionally small and only include the fields required
by the service tests. They are simple dataclasses with a helper `from_dict`
to map DB rows (or dicts returned by the repository) into typed objects.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

# Use separated model classes for clarity / extension
from .address import Address
from .ministry import Ministry
from .ministry_area import MinistryArea


@dataclass
class Person:
	person_id: Optional[int]
	first_name: Optional[str]
	last_name: Optional[str]
	email: Optional[str]
	dni: Optional[int]
	phone_number: Optional[str]



	# Address object (optional)
	address: Optional[Address] = None

	# Ministry area / ministry objects (optional)
	ministry_area: Optional[MinistryArea] = None
	ministry: Optional[Ministry] = None

	@staticmethod
	def _get(d, k, default=None):
		if d is None:
			return default
		if isinstance(d, dict):
			return d.get(k, default)
		# sqlite3.Row handling
		try:
			return d[k]
		except Exception:
			return default

	def from_dict(data: Dict[str, Any]) -> "Person":
		"""Build a Person from either a flattened dict (old style) or a
		nested structure returned by repositories:

		Example nested shape:
			{"person": {...}, "address": {...}, "area": {...}, "ministry": {...}}
		"""

		# flattened mode (backward compatibility)
		if isinstance(data, dict) and "first_name" in data:
			# build a simple Person with Address and simple area/ministry info
			addr = None
			if any(k in data for k in ("street", "neighborhood", "house_number")):
				addr = Address(
					address_id=data.get("address_id"),
					street=data.get("street"),
					neighborhood=data.get("neighborhood"),
					house_number=data.get("house_number"),
				)

			area = None
			if data.get("ministry_area") or data.get("ministry_id"):
				area = MinistryArea(
					area_id=data.get("ministry_area_id"),
					ministry_id=data.get("ministry_id"),
					area=data.get("ministry_area"),
				)

			ministry = None
			if data.get("ministry_id") or data.get("ministry"):
				ministry = Ministry(ministry_id=data.get("ministry_id"), name=data.get("ministry"))

			return Person(
				person_id=data.get("person_id"),
				first_name=data.get("first_name"),
				last_name=data.get("last_name"),
				email=data.get("email"),
				dni=data.get("dni"),
				phone_number=data.get("phone_number"),
				address=addr,
				ministry_area=area,
				ministry=ministry,
			)

		# nested mode
		p = data.get("person") if isinstance(data, dict) and "person" in data else data

		addr_data = data.get("address") if isinstance(data, dict) else None
		area_data = data.get("area") if isinstance(data, dict) else None
		ministry_data = data.get("ministry") if isinstance(data, dict) else None

		address = None
		if addr_data:
			address = Address(
				address_id=Person._get(addr_data, "address_id"),
				street=Person._get(addr_data, "street"),
				neighborhood=Person._get(addr_data, "neighborhood"),
				house_number=Person._get(addr_data, "house_number"),
			)

		area = None
		if area_data:
			area = MinistryArea(
				area_id=Person._get(area_data, "area_id"),
				ministry_id=Person._get(area_data, "ministry_id"),
				area=Person._get(area_data, "area"),
			)

		ministry = None
		if ministry_data:
			ministry = Ministry(
				ministry_id=Person._get(ministry_data, "ministry_id"),
				name=Person._get(ministry_data, "name"),
			)

		return Person(
			person_id=Person._get(p, "person_id"),
			first_name=Person._get(p, "first_name"),
			last_name=Person._get(p, "last_name"),
			email=Person._get(p, "email"),
			dni=Person._get(p, "dni"),
			phone_number=Person._get(p, "phone_number"),
			address=address,
			ministry_area=area,
			ministry=ministry,
		)


__all__ = ["Person"]

