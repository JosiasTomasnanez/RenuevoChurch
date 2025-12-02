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
