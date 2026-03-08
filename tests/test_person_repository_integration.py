from src.backend.db.db import Database
from src.backend.db.repositories import person_repository, get_area_and_ministry
from src.backend.db.repositories import ministry_repository


def _seed_db(db: Database):
    # insert minimal address, ministry_area and person
    addr_id = db.insert(
        "INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)",
        ("Calle Falsa", "Belgrano", 10),
    )

    # add a ministry and reference it from ministry_area
    min_id = db.insert("INSERT INTO ministry (name) VALUES (?)", ("Music",))
    area_id = db.insert(
        "INSERT INTO ministry_area (ministry_id, area) VALUES (?,?)", (min_id, "Worship")
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

    # add a second person that begins with a special-character surname
    person_id_2 = db.insert(
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
        (addr_id, area_id, "Jose", "Ñañez", "jose@example.com", 87654321, "555-2222"),
    )

    return addr_id, area_id, person_id, min_id


def test_repository_queries_against_temp_db(tmp_path, monkeypatch):
    # Create a temporary SQLite file and initialize schema
    db_file = tmp_path / "test.db"
    db = Database(path=db_file)
    db.initialize_schema()

    # Seed data
    addr_id, area_id, person_id, min_id = _seed_db(db)

    # Make the repository use our temporary db instance
    monkeypatch.setattr(person_repository, "db", db)

    # Query by exact neighborhood
    rows = person_repository.find_people_by_neighborhood("Belgrano")
    assert isinstance(rows, list)
    assert len(rows) == 2
    assert any(r["person"]["first_name"] == "Ana" for r in rows)

    # Query with partial match
    rows_partial = person_repository.find_people_by_neighborhood("elgra", partial=True)
    assert isinstance(rows_partial, list)
    assert len(rows_partial) == 2

    # Query by ministry id
    rows_ministry = person_repository.find_people_by_ministry(min_id)
    assert isinstance(rows_ministry, list)
    assert len(rows_ministry) == 2

    # Query area+ministry using the new repository helper
    monkeypatch.setattr(ministry_repository, "db", db)
    info = get_area_and_ministry(area_id)
    assert info is not None
    assert info["area"]["area"] == "Worship"
    assert info["area"]["ministry_id"] == min_id
    assert info["ministry"]["name"] == "Music"

    # ---- Informational output (useful when running tests with -s or CI logs) ----
    # Provide a short summary of what the test executed and what was returned.
    print("\n[INTEGRATION TEST] person_repository queries against temporary DB")
    print(f"DB file: {db.path}")
    print(f"Exact neighborhood 'Belgrano' -> {len(rows)} row(s)")
    # print first row in readable dict form
    if rows:
        print("  first row:", rows[0])
    print(f"Partial neighborhood 'elgra' -> {len(rows_partial)} row(s)")
    print(f"Ministry id 1 -> {len(rows_ministry)} row(s)")
    print("Area/ministry lookup ->", info)

    # Query people by name (prefix semantics)
    rows_name_prefix = person_repository.find_people_by_name("An", partial=True)
    assert isinstance(rows_name_prefix, list)
    assert len(rows_name_prefix) == 1

    # a substring that does not match the start should not return results
    rows_name_sub = person_repository.find_people_by_name("na", partial=True)
    assert isinstance(rows_name_sub, list)
    assert len(rows_name_sub) == 0

    # exact match
    rows_name_exact = person_repository.find_people_by_name("Ana", partial=False)
    assert len(rows_name_exact) == 1

    # special-case: prefix search with 'ña' should match last_name 'Ñañez'
    rows_name_ña = person_repository.find_people_by_name("ña", partial=True)
    assert len(rows_name_ña) == 1
    assert rows_name_ña[0]["person"]["last_name"] == "Ñañez"


def test_delete_person_removes_orphan_address(tmp_path):
    """Verify delete_person removes the person and deletes an orphaned address
    but does not delete an address shared by other people.
    """
    db_file = tmp_path / "del.db"
    db = Database(path=db_file)
    db.initialize_schema()

    # create a unique address and person
    addr_id = db.insert("INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)", ("Solo St", "Uno", 1))
    pid = db.insert("INSERT INTO person (address_id, first_name) VALUES (?,?)", (addr_id, "Solo"))

    # delete the person; since address is unique it should be removed too
    # ensure the repository module uses this db instance
    from src.backend.db.repositories import person_repository as repo
    repo.db = db

    ok = repo.delete_person(pid)
    assert ok is True

    row = db.query_one("SELECT * FROM person WHERE person_id = ?", (pid,))
    assert row is None

    addr = db.query_one("SELECT * FROM address WHERE address_id = ?", (addr_id,))
    assert addr is None


def test_delete_person_shared_address(tmp_path):
    """If two people share the same address, deleting one should not remove the address."""
    db_file = tmp_path / "shared.db"
    db = Database(path=db_file)
    db.initialize_schema()

    addr_id = db.insert("INSERT INTO address (street, neighborhood, house_number) VALUES (?,?,?)", ("Shared St", "Dos", 2))
    p1 = db.insert("INSERT INTO person (address_id, first_name) VALUES (?,?)", (addr_id, "A"))
    p2 = db.insert("INSERT INTO person (address_id, first_name) VALUES (?,?)", (addr_id, "B"))

    from src.backend.db.repositories import person_repository as repo
    repo.db = db

    ok = repo.delete_person(p1)
    assert ok is True

    remaining = db.query_one("SELECT * FROM person WHERE person_id = ?", (p2,))
    assert remaining is not None

    addr = db.query_one("SELECT * FROM address WHERE address_id = ?", (addr_id,))
    assert addr is not None

    # -------- Test delete behavior from repository module-level helper --------
    # delete the first person (p1) — because p2 still references the same
    # address the address should remain
    deleted = person_repository.delete_person(p1)
    assert deleted is True

    remaining = person_repository.find_all_people()
    assert len(remaining) == 1

    # address still exists because p2 still references it
    addr_row = db.query_one("SELECT * FROM address WHERE address_id = ?", (addr_id,))
    assert addr_row is not None

    # delete the remaining person (p2) — this should remove the person and
    # the address since no other person references it
    deleted2 = person_repository.delete_person(p2)
    assert deleted2 is True

    final_people = person_repository.find_all_people()
    assert len(final_people) == 0

    # address should now be gone
    addr_row2 = db.query_one("SELECT * FROM address WHERE address_id = ?", (addr_id,))
    assert addr_row2 is None

