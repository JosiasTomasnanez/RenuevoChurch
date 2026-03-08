from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Optional, Dict
import importlib

from .config import AppConfig, create_database, create_services


@dataclass
class App:
	"""Application container holding runtime objects.

	- config: AppConfig used to create the app
	- db: Database instance used by repositories/services
	- services: SimpleNamespace holding service modules
	- controllers: mapping of controller name -> module (wired with services)
	"""

	config: AppConfig
	db: object
	services: SimpleNamespace
	controllers: Dict[str, object]


def _wire_controllers(services: SimpleNamespace) -> Dict[str, object]:
	"""Import frontend controllers and attach the services namespace.

	Controllers are simple modules in the `src.frontend.controllers` package.
	We attach a `services` attribute to each module so the frontend code can
	access the service helpers without needing to manage construction.
	"""
	controllers = {}
	controller_modules = (
		"src.frontend.controllers.person_controller",
	)

	for name in controller_modules:
		try:
			mod = importlib.import_module(name)
			# Expose the services object directly on the controller module
			setattr(mod, "services", services)
			controllers[name.split(".")[-1]] = mod
		except Exception:
			# If controller module is not available, skip gracefully.
			# This keeps the app resilient during development.
			continue

	return controllers


def create_app(config: Optional[AppConfig] = None, override_db: Optional[object] = None) -> App:
	"""Factory: build the Database, services and wire controllers.

	- config: optional AppConfig; if omitted defaults are used
	- override_db: optionally pass a Database instance (useful for tests / in-memory DB)
	"""
	config = config or AppConfig()

	# Create and install selected database into repository modules
	db_instance = create_database(config, override_db)

	# Create services container (modules)
	services = create_services()

	# Wire services into controllers so the frontend can call them
	controllers = _wire_controllers(services)

	return App(config=config, db=db_instance, services=services, controllers=controllers)


__all__ = ["create_app", "App"]

