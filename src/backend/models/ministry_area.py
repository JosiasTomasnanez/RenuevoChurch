"""MinistryArea model (separate file)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MinistryArea:
    area_id: Optional[int]
    ministry_id: Optional[int]
    area: Optional[str]


__all__ = ["MinistryArea"]
