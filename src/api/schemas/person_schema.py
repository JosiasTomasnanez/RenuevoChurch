from pydantic import BaseModel
from typing import Optional


class PersonResponse(BaseModel):
    person_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone_number: Optional[str] = None
    dni: Optional[int] = None

    class Config:
        from_attributes = True
