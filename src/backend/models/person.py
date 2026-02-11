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
	birthdate: Optional[str]
	dni: Optional[int]
	phone_number: Optional[str]
	marital_status: Optional[str]
	social_security: Optional[str]
	baptized: Optional[bool]
	cdb: Optional[int]  # CDB house ID (foreign key to cdb table, can be None)
	# Foreign keys
	address_id: Optional[int]
	trusted_person_id: Optional[int]
	ministry_id: Optional[int]
	ministry_area_id: Optional[int]
	consolidation_id: Optional[int]
	future_ministry_area_id: Optional[int]

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
				birthdate=data.get("birthdate"),
				dni=data.get("dni"),
				phone_number=data.get("phone_number"),
				marital_status=data.get("marital_status"),
				social_security=data.get("social_security"),
				baptized=data.get("baptized"),
				cdb=data.get("cdb"),
				address_id=data.get("address_id"),
				trusted_person_id=data.get("trusted_person_id"),
				ministry_id=data.get("direct_ministry_id"),  # Direct ministry assignment
				ministry_area_id=data.get("ministry_area_id"),
				consolidation_id=data.get("consolidation_id"),
				future_ministry_area_id=data.get("future_ministry_area_id"),
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
			birthdate=Person._get(p, "birthdate"),
			dni=Person._get(p, "dni"),
			phone_number=Person._get(p, "phone_number"),
			marital_status=Person._get(p, "marital_status"),
			social_security=Person._get(p, "social_security"),
			baptized=Person._get(p, "baptized"),
			cdb=Person._get(p, "cdb"),
			address_id=Person._get(p, "address_id"),
			trusted_person_id=Person._get(p, "trusted_person_id"),
			ministry_id=Person._get(p, "ministry_id"),
			ministry_area_id=Person._get(p, "ministry_area_id"),
			consolidation_id=Person._get(p, "consolidation_id"),
			future_ministry_area_id=Person._get(p, "future_ministry_area_id"),
			address=address,
			ministry_area=area,
			ministry=ministry,
		)


__all__ = ["Person"]

