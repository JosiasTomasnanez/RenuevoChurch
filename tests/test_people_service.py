import pytest


from src.backend.services.people import (
    get_people_by_neighborhood,
    get_people_by_ministry,
    get_people_by_name,
    get_all_people,
)
from src.backend.models.person import Person


SAMPLE_ROW = {
    "person_id": 1,
    "first_name": "Ana",
    "last_name": "Gomez",
    "email": "ana@example.com",
    "dni": 12345678,
    "phone_number": "555-1111",
    "street": "Calle Falsa",
    "neighborhood": "Belgrano",
    "house_number": 10,
    "ministry_area": "Worship",
    "ministry_id": 2,
}


def test_get_people_by_neighborhood_monkeypatch(monkeypatch):
    called = {}


    def fake_find(neighborhood, partial=False):
        called["neighborhood"] = neighborhood
        called["partial"] = partial
        return [SAMPLE_ROW]


    # service imports the repository functions directly, so patch the names
    # on the service module where they're used
    monkeypatch.setattr(
        "src.backend.services.people.find_people_by_neighborhood", fake_find
    )

    result = get_people_by_neighborhood("Belgrano")
    assert isinstance(result, list)
    assert len(result) == 1
    person = result[0]
    assert isinstance(person, Person)
    assert person.first_name == "Ana"
    # address is now a nested object
    assert person.address is not None
    assert person.address.neighborhood == "Belgrano"
    assert called["neighborhood"] == "Belgrano"
    assert called["partial"] is False


def test_get_people_by_ministry_monkeypatch(monkeypatch):
    def fake_find(ministry_id):
        assert ministry_id == 2
        return [SAMPLE_ROW]


    monkeypatch.setattr(
        "src.backend.services.people.find_people_by_ministry", fake_find
    )

    result = get_people_by_ministry(2)
    assert isinstance(result, list)
    assert len(result) == 1
    person = result[0]
    assert isinstance(person, Person)
    # ministry area and ministry are now nested objects
    assert person.ministry is not None
    assert person.ministry.ministry_id == 2
    assert person.ministry_area is not None
    assert person.ministry_area.area == "Worship"


def test_get_people_by_name_monkeypatch(monkeypatch):
    called = {}

    def fake_find(name, partial=True):
        called["name"] = name
        called["partial"] = partial
        return [SAMPLE_ROW]

    monkeypatch.setattr("src.backend.services.people.find_people_by_name", fake_find)

    result = get_people_by_name("Ana")
    assert isinstance(result, list)
    assert len(result) == 1
    person = result[0]
    assert isinstance(person, Person)
    assert person.first_name == "Ana"
    # service normalizes the query before calling repository (strip only)
    assert called["name"] == "Ana"
    assert called["partial"] is True


def test_get_all_people_monkeypatch(monkeypatch):
    called = {}

    def fake_all():
        called['all'] = True
        return [SAMPLE_ROW]

    monkeypatch.setattr("src.backend.services.people.find_all_people", fake_all)

    result = get_all_people()
    assert isinstance(result, list)
    assert len(result) == 1
    assert called.get('all') is True


def test_get_people_by_name_unicode_casefold(monkeypatch):
    # repository returns a row with a last_name containing 'Ñ' uppercase
    row = {
        "person": {
            "person_id": 2,
            "first_name": "Jose",
            "last_name": "Ñañez",
            "email": "jose@example.com",
            "dni": 11111111,
            "phone_number": "555-2222",
        },
        "address": {"neighborhood": "Centro"},
    }

    def fake_find(name, partial=True):
        # repository originally returns the row irrespective of case —
        # service performs the casefold-based check
        return [row]

    monkeypatch.setattr("src.backend.services.people.find_people_by_name", fake_find)

    # searching with lower-case 'ña' should match last_name 'Ñañez'
    result = get_people_by_name("ña")
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0].last_name == "Ñañez"


def test_get_people_by_name_trims_and_lower(monkeypatch):
    called = {}

    def fake_find(name, partial=True):
        called['name'] = name
        return []

    monkeypatch.setattr("src.backend.services.people.find_people_by_name", fake_find)

    get_people_by_name("  JoE  ")
    # service sends stripped (but not lowercased) value to repository
    assert called['name'] == 'JoE'
