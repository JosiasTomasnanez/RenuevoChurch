from pydantic import BaseModel


# ================================
# Ministries
# ================================

class MinistryCreate(BaseModel):
    name: str


class MinistryUpdate(BaseModel):
    name: str


class MinistryResponse(BaseModel):
    ministry_id: int
    name: str


# ================================
# Areas
# ================================

class AreaCreate(BaseModel):
    ministry_id: int
    area: str


class AreaUpdate(BaseModel):
    area: str


class AreaResponse(BaseModel):
    area_id: int
    ministry_id: int
    area: str


# ================================
# Consolidations
# ================================

class ConsolidationCreate(BaseModel):
    level: str


class ConsolidationUpdate(BaseModel):
    level: str


class ConsolidationResponse(BaseModel):
    consolidation_id: int
    level: str


# ================================
# CDB
# ================================

class CdbCreate(BaseModel):
    number: str


class CdbUpdate(BaseModel):
    number: str


class CdbResponse(BaseModel):
    cdb_id: int
    number: str

# ================================
# Occupations
# ================================

class OccupationCreate(BaseModel):
    name: str


class OccupationUpdate(BaseModel):
    name: str


class OccupationResponse(BaseModel):
    occupation_id: int
    name: str