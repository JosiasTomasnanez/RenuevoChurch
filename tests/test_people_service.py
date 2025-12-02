import pytest


from src.backend.services.people import (
    get_people_by_neighborhood,
    get_people_by_ministry,
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
