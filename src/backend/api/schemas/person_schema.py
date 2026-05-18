from pydantic import BaseModel
from typing import Optional, List


# =================================
# Occupation (Master Catalog)
# =================================

class OccupationBase(BaseModel):
    name: str

class OccupationCreate(OccupationBase):
    pass

class OccupationUpdate(OccupationBase):
    pass

class OccupationResponse(OccupationBase):
    occupation_id: int

    class Config:
        from_attributes = True


# =================================
# Membership
# =================================

class Membership(BaseModel):
    ministry_id: int
    area_id: Optional[int] = None
    is_primary: Optional[bool] = False


# =================================
# Create Person
# =================================

class PersonCreate(BaseModel):

    first_name: str
    last_name: str
    gender: Optional[str] = None

    email: Optional[str] = None
    birthdate: Optional[str] = None
    dni: Optional[int] = None
    phone_number: Optional[str] = None

    marital_status: Optional[str] = None
    membership_status: Optional[str] = None

    social_security: Optional[str] = None
    baptized: Optional[bool] = None
    cdb: Optional[int] = None
    consolidation_id: Optional[int] = None
    trusted_person_info: Optional[str] = None

    street: Optional[str] = None
    house_number: Optional[int] = None
    neighborhood: Optional[str] = None

    memberships: Optional[List[Membership]] = None
    occupation_ids: Optional[List[int]] = None  # IDs elegidos en la interfaz


# =================================
# Update Person
# =================================

class PersonUpdate(BaseModel):

    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None

    email: Optional[str] = None
    birthdate: Optional[str] = None
    dni: Optional[int] = None
    phone_number: Optional[str] = None

    marital_status: Optional[str] = None
    membership_status: Optional[str] = None

    social_security: Optional[str] = None
    baptized: Optional[bool] = None
    cdb: Optional[int] = None
    consolidation_id: Optional[int] = None
    trusted_person_info: Optional[str] = None

    street: Optional[str] = None
    house_number: Optional[int] = None
    neighborhood: Optional[str] = None

    memberships: Optional[List[Membership]] = None
    occupation_ids: Optional[List[int]] = None  # IDs para actualizar la relación


# =================================
# Response Person
# =================================

class PersonResponse(BaseModel):

    person_id: int
    first_name: str
    last_name: str
    gender: Optional[str] = None

    email: Optional[str] = None
    dni: Optional[str] = None
    phone_number: Optional[str] = None

    marital_status: Optional[str] = None
    membership_status: Optional[str] = None

    trusted_person_info: Optional[str] = None

    street: Optional[str] = None
    house_number: Optional[str] = None
    neighborhood: Optional[str] = None
    occupations: Optional[List[OccupationResponse]] = None  