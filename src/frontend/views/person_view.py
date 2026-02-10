"""Orchestrator module that re-exports the person-related frames.

This module keeps the previous public API (AddPersonFrame, SearchPersonFrame,
ModifyPersonFrame) while placing each frame implementation in its own file.
It makes imports in other modules (like `src.frontend.main`) unchanged.
"""

from .add_person_view import AddPersonFrame
from .search_person_view import SearchPersonFrame
from .modify_person_view import ModifyPersonFrame

__all__ = ["AddPersonFrame", "SearchPersonFrame", "ModifyPersonFrame"]


