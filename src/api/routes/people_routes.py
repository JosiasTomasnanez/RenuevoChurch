from fastapi import APIRouter
from src.backend.app.main import services
from src.api.schemas.person_schema import PersonResponse

router = APIRouter(prefix="/people", tags=["People"])


@router.get("/", response_model=list[PersonResponse])
def get_all_people():
    return services.people.get_all_people()


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(person_id: int):
    return services.people.get_person(person_id)
