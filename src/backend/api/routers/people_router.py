from fastapi import APIRouter, Body, HTTPException
from typing import Any, List, Optional
import logging

from src.backend.services import people as service
from src.backend.api.schemas.person_schema import Membership, PersonCreate, PersonUpdate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/people",
    tags=["people"]
)

# -----------------------------------
# Create person
# -----------------------------------
@router.post("/")
def create_person(payload: PersonCreate):
    try:
        data = payload.model_dump(exclude_unset=True)
        memberships = data.pop("memberships", None)

        person_id = service.create_person(data)

        if memberships:
            service.update_person_memberships(
                person_id,
                [m.model_dump() for m in memberships],
            )
        return person_id   # <- solo el número
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# -----------------------------------
# Get all people
# -----------------------------------
@router.get("/")
def get_all_people():
    return service.get_all_people()


# -----------------------------------
# Search people
# -----------------------------------
@router.get("/search")
def search_people(query: str, partial: bool = True):
    try:
        if not query:
            return service.get_all_people()
        return service.get_people_by_name(query, partial)
    except Exception:
        raise HTTPException(status_code=500, detail="Search failed")


# -----------------------------------
# Get one person
# -----------------------------------
@router.get("/{person_id}")
def get_person(person_id: int):
    person = service.get_person(person_id)

    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")

    return person


# -----------------------------------
# Update person
# -----------------------------------
@router.put("/{person_id}")
def update_person(person_id: int, payload: PersonUpdate):

    try:
        data = payload.model_dump(exclude_unset=True)
        memberships = data.pop("memberships", None)

        ok = service.update_person(person_id, data)

        if not ok:
            raise HTTPException(status_code=404, detail="Person not found")

        if memberships is not None:
            service.update_person_memberships(
                person_id,
                [m.model_dump() for m in memberships],
            )

        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------------
# Delete person
# -----------------------------------
@router.delete("/{person_id}")
def delete_person(person_id: int):

    ok = service.delete_person(person_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Person not found")

    return {"status": "deleted"}


# -----------------------------------
# Get people by ministry
# -----------------------------------
@router.get("/by-ministry/{ministry_id}")
def get_people_by_ministry(ministry_id: int):

    return service.get_people_by_ministry(ministry_id)


# -----------------------------------
# Get memberships for person
# -----------------------------------
@router.get("/{person_id}/memberships")
def get_memberships(person_id: int):

    return service.get_memberships_for_person(person_id)


# -----------------------------------
# Replace memberships for person
# -----------------------------------
@router.put("/{person_id}/memberships")
def update_memberships(
    person_id: int,
    payload: Any = Body(default_factory=list),
):
    logger.info(f"Updating memberships for person {person_id} with payload: {payload}")
    try:
        # Be liberal in what we accept:
        # - JSON array: [{"ministry_id": 1, "area_id": null}, ...]
        # - JSON object: {"memberships": [...]} (some clients may wrap)
        memberships_raw = payload
        if isinstance(payload, dict) and "memberships" in payload:
            memberships_raw = payload.get("memberships")

        if memberships_raw is None:
            memberships_raw = []
        if not isinstance(memberships_raw, list):
            raise HTTPException(status_code=422, detail="memberships must be a JSON array")

        memberships = [Membership.model_validate(m) for m in memberships_raw]
        logger.info(f"Validated memberships: {memberships}")
        service.update_person_memberships(
            person_id,
            [m.model_dump() for m in (memberships or [])],
        )
        return {"status": "updated"}
    except Exception as e:
        logger.error(f"Error updating memberships for person {person_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
