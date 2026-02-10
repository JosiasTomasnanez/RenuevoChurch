from src.frontend.controllers.person_controller import PersonController


SAMPLE_PERSON = {
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
            return [SAMPLE_PERSON]

    # services object should have a .people attribute (matching app.services)
    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(services=services)

    results = ctrl.search('Ana')
    assert isinstance(results, list)
    assert len(results) == 1
    assert called['name'] == 'Ana'
    assert called['partial'] is True


def test_controller_search_returns_empty_when_no_query():
    # When services not present, return empty list
    from types import SimpleNamespace
    services = SimpleNamespace(people=None)
    ctrl = PersonController(services=services)
    assert ctrl.search('') == []


def test_controller_search_empty_returns_all(monkeypatch):
    called = {}

    class FakeService:
        def get_all_people(self):
            called['all'] = True
            return [SAMPLE_PERSON]

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(services=services)

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
    ctrl = PersonController(services=services)

    ok = ctrl.delete_person(5)
    assert ok is True
    assert called['pid'] == 5


def test_controller_add_person_calls_service(monkeypatch):
    called = {}

    class FakeService:
        def create_person(self, payload):
            called['payload'] = payload
            return 42

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(services=services)

    person_id = ctrl.add_person({"first_name": "Juan", "last_name": "Perez"})
    assert person_id == 42
    assert called['payload'] == {"first_name": "Juan", "last_name": "Perez"}


def test_controller_get_person_calls_service(monkeypatch):
    called = {}

    class FakePerson:
        def __init__(self):
            self.person_id = 1
            self.first_name = "Ana"

    class FakeService:
        def get_person(self, person_id):
            called['person_id'] = person_id
            return FakePerson()

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(services=services)

    person = ctrl.get_person(1)
    assert person is not None
    assert person.first_name == "Ana"
    assert called['person_id'] == 1


def test_controller_update_person_calls_service(monkeypatch):
    called = {}

    class FakeService:
        def update_person(self, person_id, payload):
            called['person_id'] = person_id
            called['payload'] = payload
            return True

    from types import SimpleNamespace
    services = SimpleNamespace(people=FakeService())
    ctrl = PersonController(services=services)

    ok = ctrl.update_person(1, {"first_name": "Juan"})
    assert ok is True
    assert called['person_id'] == 1
    assert called['payload'] == {"first_name": "Juan"}

