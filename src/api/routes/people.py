from fastapi import APIRouter, Request
from src.api.schemas.person_schema import PersonResponse

router = APIRouter()


@router.get("/", response_model=list[PersonResponse])
def get_all_people(request: Request):
    services = request.app.state.services
    return services.people.get_all_people()


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int, request: Request):
    services = request.app.state.services
    return services.people.get_person(person_id)
