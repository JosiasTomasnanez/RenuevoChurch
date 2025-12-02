from src.frontend.controllers.person_controller import PersonController


SAMPLE_ROW = {
    "person": {
        "person_id": 1,
        "first_name": "Ana",
        "last_name": "Gomez",
        "email": "ana@example.com",
        "dni": 12345678,
        "phone_number": "555-1111",
    },
    "address": {"neighborhood": "Belgrano"},
}


def test_controller_search_calls_name_service(monkeypatch):
    called = {}

    class FakeService:
        def get_people_by_name(self, name, partial=True):
            called['name'] = name
            called['partial'] = partial
            return [SAMPLE_ROW]

    # services object should have a .people attribute (matching app.services)
    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(db=None, services=services)

    results = ctrl.search('Ana')
    assert isinstance(results, list)
    assert len(results) == 1
    assert called['name'] == 'Ana'
    assert called['partial'] is True


def test_controller_search_returns_empty_when_no_query():
    # When services not present, return empty list
    ctrl = PersonController(db=None, services=None)
    assert ctrl.search('') == []


def test_controller_search_empty_returns_all(monkeypatch):
    called = {}

    class FakeService:
        def get_all_people(self):
            called['all'] = True
            return [SAMPLE_ROW]

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(db=None, services=services)

    results = ctrl.search('')
    assert isinstance(results, list)
    assert len(results) == 1
    assert called.get('all') is True


def test_controller_delete_calls_service(monkeypatch):
    called = {}

    class FakeService:
        def delete_person(self, pid):
            called['pid'] = pid
            return True

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(db=None, services=services)

    ok = ctrl.delete_person(5)
    assert ok is True
    assert called['pid'] == 5


def test_controller_delete_fallback(monkeypatch, tmp_path):
    # Use a real temporary DB for fallback path
    from src.backend.db.db import Database

    db_file = tmp_path / "test.db"
    db = Database(path=db_file)
    db.initialize_schema()

    # insert an address and person
    addr_id = db.insert("INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)", ("Calle", "X", 1))
    pid = db.insert("INSERT INTO person (address_id, first_name) VALUES (?,?)", (addr_id, "Tom"))

    # construct controller that will exercise fallback delete
    ctrl = PersonController(db=db, services=None)
    ok = ctrl.delete_person(pid)
    assert ok is True

    # person should be gone
    row = db.query_one("SELECT * FROM person WHERE person_id = ?", (pid,))
    assert row is None
    # address should be removed because no other person references it
    addr = db.query_one("SELECT * FROM address WHERE address_id = ?", (addr_id,))
    assert addr is None
