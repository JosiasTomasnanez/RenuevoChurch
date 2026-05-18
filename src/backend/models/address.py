"""Address model (separate file for clarity and future extension)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Address:
    address_id: Optional[int]
    street: Optional[str]
    neighborhood: Optional[str]
    house_number: Optional[int]


__all__ = ["Address"]
