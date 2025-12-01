from src.backend.db.db import Database
from src.backend.db.repositories import person_repository, get_area_and_ministry_by_area_id
from src.backend.db.repositories import ministry_repository


def _seed_db(db: Database):
    # insert minimal address, ministry_area and person
    addr_id = db.insert(
        "INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)",
        ("Calle Falsa", "Belgrano", 10),
    )

    area_id = db.insert(
        "INSERT INTO ministry_area (ministry_id, area) VALUES (?,?)", (1, "Worship")
    )

    person_id = db.insert(
        """
        INSERT INTO person (
            address_id,
            ministry_area_id,
            first_name,
            last_name,
            email,
            dni,
            phone_number
        ) VALUES (?,?,?,?,?,?,?)
        """,
        (addr_id, area_id, "Ana", "Gomez", "ana@example.com", 12345678, "555-1111"),
    )

    return addr_id, area_id, person_id


def test_repository_queries_against_temp_db(tmp_path, monkeypatch):
    # Create a temporary SQLite file and initialize schema
    db_file = tmp_path / "test.db"
    db = Database(path=db_file)
    db.initialize_schema()

    # Seed data
    addr_id, area_id, person_id = _seed_db(db)

    # Make the repository use our temporary db instance
    monkeypatch.setattr(person_repository, "db", db)

    # Query by exact neighborhood
    rows = person_repository.find_people_by_neighborhood("Belgrano")
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["first_name"] == "Ana"

    # Query with partial match
    rows_partial = person_repository.find_people_by_neighborhood("elgra", partial=True)
    assert isinstance(rows_partial, list)
    assert len(rows_partial) == 1

    # Query by ministry id
    rows_ministry = person_repository.find_people_by_ministry(1)
    assert isinstance(rows_ministry, list)
    assert len(rows_ministry) == 1

    # Query area+ministry using the new repository helper
    monkeypatch.setattr(ministry_repository, "db", db)
    info = get_area_and_ministry_by_area_id(area_id)
    assert info is not None
    assert info["area"] == "Worship"
    assert info["ministry_id"] == 1

    # ---- Informational output (useful when running tests with -s or CI logs) ----
    # Provide a short summary of what the test executed and what was returned.
    print("\n[INTEGRATION TEST] person_repository queries against temporary DB")
    print(f"DB file: {db.path}")
    print(f"Exact neighborhood 'Belgrano' -> {len(rows)} row(s)")
    # print first row in readable dict form
    if rows:
        print("  first row:", dict(rows[0]))
    print(f"Partial neighborhood 'elgra' -> {len(rows_partial)} row(s)")
    print(f"Ministry id 1 -> {len(rows_ministry)} row(s)")
    print("Area/ministry lookup ->", info)

