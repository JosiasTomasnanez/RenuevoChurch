"""Ministry model (separate file)."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Ministry:
    ministry_id: Optional[int]
    name: Optional[str]


__all__ = ["Ministry"]
