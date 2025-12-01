"""Tiny models used by the People service and tests.

These models are intentionally small and only include the fields required
by the service tests. They are simple dataclasses with a helper `from_dict`
to map DB rows (or dicts returned by the repository) into typed objects.
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Person:
	person_id: Optional[int]
	first_name: Optional[str]
	last_name: Optional[str]
	email: Optional[str]
	dni: Optional[int]
	phone_number: Optional[str]

	# Address / neighborhood convenience fields returned by repository
	street: Optional[str] = None
	neighborhood: Optional[str] = None
	house_number: Optional[int] = None

	# Ministry area info (optional)
	ministry_area: Optional[str] = None
	ministry_id: Optional[int] = None

	@staticmethod
	def from_dict(data: Dict[str, Any]) -> "Person":
		# Defensive fetching in case data comes as sqlite3.Row or plain dict
		get = data.get if isinstance(data, dict) else lambda k, d=None: data[k] if k in data.keys() else d

		return Person(
			person_id=get("person_id"),
			first_name=get("first_name"),
			last_name=get("last_name"),
			email=get("email"),
			dni=get("dni"),
			phone_number=get("phone_number"),
			street=get("street"),
			neighborhood=get("neighborhood"),
			house_number=get("house_number"),
			ministry_area=get("ministry_area"),
			ministry_id=get("ministry_id"),
		)


__all__ = ["Person"]

