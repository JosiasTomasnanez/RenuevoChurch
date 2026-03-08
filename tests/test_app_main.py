from src.backend.app.main import create_app
from src.backend.app.config import AppConfig


def test_create_app_wires_services_to_controllers(tmp_path):
    # Avoid mutating the default filesystem DB during tests
    cfg = AppConfig(initialize_schema=False)
    app = create_app(config=cfg)

    # Services container must expose the people service module
    assert hasattr(app.services, "people")

    # The frontend controller module should have been wired with the same
    # services object by the application factory.
    import importlib

    mod = importlib.import_module("src.frontend.controllers.person_controller")
    assert getattr(mod, "services") is app.services


def test_create_app_respects_db_override():
    # Provide an in-memory Database instance and ensure the app & repos use it
    from src.backend.db.db import Database

    mem = Database(path=":memory:")

    app = create_app(config=AppConfig(initialize_schema=False), override_db=mem)
    assert app.db is mem

    # repositories should also reference the same instance
    import importlib

    person_repo = importlib.import_module("src.backend.db.repositories.person_repository")
    assert getattr(person_repo, "db") is mem
