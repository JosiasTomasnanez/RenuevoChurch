from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from pathlib import Path
from typing import Optional
import importlib

from src.backend.db.db import Database


@dataclass
class AppConfig:
	"""Simple configuration container for the application.

	- db_path: optional path to the sqlite database file. If None, the
	  default path (data/renuevo.db) is used.
	- initialize_schema: when True the schema will be created on startup.
	"""

	db_path: Optional[str] = None
	initialize_schema: bool = True


def _ensure_db_visible_to_repos(db_instance: Database) -> None:
	"""Make repository modules use the provided Database instance.

	Repositories import the module that exposes the top-level `db` value.
	When tests or callers pass a custom Database instance we must make
	sure both the db module and the already-imported repository modules
	get the updated instance so calls flow to the intended DB.
	"""
	# Ensure the canonical db module object exposes the instance
	db_module = importlib.import_module("src.backend.db.db")
	setattr(db_module, "db", db_instance)

	# Update known repository modules so their module-level `db` variable
	# points to the same instance (repositories often cache a reference).
	repo_modules = (
		"src.backend.db.repositories.person_repository",
		"src.backend.db.repositories.ministry_repository",
	)

	for mod_name in repo_modules:
		try:
			repo_mod = importlib.import_module(mod_name)
			setattr(repo_mod, "db", db_instance)
		except Exception:
			# be permissive — if the module isn't imported yet it's fine
			# it will pick up the new db via the db module when it imports
			pass


def create_database(config: AppConfig, override_db: Optional[Database] = None) -> Database:
	"""Return a Database instance ready to use by the application.

	If override_db is provided it will be used directly (useful for tests)
	otherwise a Database pointing to config.db_path will be created.

	The function also ensures the repository modules and the db module
	point at the chosen instance so service code will operate against it.
	"""
	if override_db is not None:
		db_instance = override_db
	else:
		db_path = Path(config.db_path) if config.db_path else None
		db_instance = Database(path=db_path)

	_ensure_db_visible_to_repos(db_instance)

	if config.initialize_schema:
		# Create tables if missing (idempotent)
		db_instance.initialize_schema()

	return db_instance


def create_services() -> SimpleNamespace:
	"""Create a simple services container (module wrappers).

	Services in this project are currently thin module-level helpers. This
	function returns a SimpleNamespace with those modules attached so the
	caller can pass them around as a single 'services' object.
	"""
	people = importlib.import_module("src.backend.services.people")
	return SimpleNamespace(people=people)


__all__ = ["AppConfig", "create_database", "create_services"]


