from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.backend.services.config import ConfigService
from src.backend.api.schemas.config_schema import (
    MinistryCreate, MinistryUpdate,
    AreaCreate, AreaUpdate,
    ConsolidationCreate, ConsolidationUpdate,
    CdbCreate, CdbUpdate
)
class MaritalStatusCreate(BaseModel):
    name: str

class MembershipStatusCreate(BaseModel):
    name: str

router = APIRouter(
    prefix="/config",
    tags=["config"]
)
    
service = ConfigService()

# ================================
# Ministries
# ================================

@router.get("/ministries")
def get_all_ministries():
    return service.get_all_ministries()


@router.post("/ministries")
def create_ministry(data: MinistryCreate):
    return {"ministry_id": service.create_ministry(data.name)}


@router.put("/ministries/{ministry_id}")
def update_ministry(ministry_id: int, data: MinistryUpdate):

    ok = service.update_ministry(ministry_id, data.name)

    if not ok:
        raise HTTPException(status_code=404, detail="Ministry not found")

    return {"status": "updated"}


@router.delete("/ministries/{ministry_id}")
def delete_ministry(ministry_id: int):

    ok = service.delete_ministry(ministry_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Ministry not found")

    return {"status": "deleted"}


# ================================
# Areas
# ================================

@router.get("/areas/by-ministry/{ministry_id}")
def get_areas_by_ministry(ministry_id: int):
    return service.get_areas_by_ministry(ministry_id)


@router.post("/areas")
def create_area(data: AreaCreate):
    return {"area_id": service.create_area(data.ministry_id, data.area)}


@router.put("/areas/{area_id}")
def update_area(area_id: int, data: AreaUpdate):

    ok = service.update_area(area_id, data.area)

    if not ok:
        raise HTTPException(status_code=404, detail="Area not found")

    return {"status": "updated"}


@router.delete("/areas/{area_id}")
def delete_area(area_id: int):

    ok = service.delete_area(area_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Area not found")

    return {"status": "deleted"}


# ================================
# Consolidations
# ================================

@router.get("/consolidations")
def get_all_consolidations():
    return service.get_all_consolidations()


@router.post("/consolidations")
def create_consolidation(data: ConsolidationCreate):
    return {"consolidation_id": service.create_consolidation(data.level)}


@router.put("/consolidations/{consolidation_id}")
def update_consolidation(consolidation_id: int, data: ConsolidationUpdate):

    ok = service.update_consolidation(consolidation_id, data.level)

    if not ok:
        raise HTTPException(status_code=404, detail="Consolidation not found")

    return {"status": "updated"}


@router.delete("/consolidations/{consolidation_id}")
def delete_consolidation(consolidation_id: int):

    ok = service.delete_consolidation(consolidation_id)

    if not ok:
        raise HTTPException(status_code=404, detail="Consolidation not found")

    return {"status": "deleted"}


# ================================
# CDB
# ================================

@router.get("/cdb")
def get_all_cdb():
    return service.get_all_cdb_options()


@router.get("/cdb/{cdb_id}")
def get_cdb_by_id(cdb_id: int):

    cdb = service.get_cdb_by_id(cdb_id)

    if cdb is None:
        raise HTTPException(status_code=404, detail="CDB not found")

    return cdb


@router.post("/cdb")
def create_cdb(data: CdbCreate):
    return {"cdb_id": service.create_cdb(data.number)}


@router.put("/cdb/{cdb_id}")
def update_cdb(cdb_id: int, data: CdbUpdate):

    ok = service.update_cdb(cdb_id, data.number)

    if not ok:
        raise HTTPException(status_code=404, detail="CDB not found")

    return {"status": "updated"}


@router.delete("/cdb/{cdb_id}")
def delete_cdb(cdb_id: int):

    ok = service.delete_cdb(cdb_id)

    if not ok:
        raise HTTPException(status_code=404, detail="CDB not found")

    return {"status": "deleted"}

# ================================
# Marital Status
# ================================

@router.get("/marital-statuses")
def get_marital_statuses():
    """Endpoint para obtener la lista de estados civiles."""
    return service.get_marital_statuses()

@router.post("/marital-statuses")
def create_marital_status(data: MaritalStatusCreate): 
    """Endpoint para crear un nuevo estado civil."""
    return {"id": service.create_marital_status(data.name)}

@router.delete("/marital-statuses/{status_id}")
def delete_marital_status(status_id: int):
    """Endpoint para eliminar un estado civil."""
    ok = service.delete_marital_status(status_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Status not found")
    return {"status": "deleted"}

# ================================
# Membership Status
# ================================

@router.get("/membership-statuses")
def get_membership_statuses():
    """Endpoint para obtener la lista de estados de membresía."""
    return service.get_membership_statuses()


@router.post("/membership-statuses")
def create_membership_status(data: MembershipStatusCreate):
    """Endpoint para crear un nuevo estado de membresía."""

    return {
        "id": service.create_membership_status(data.name)
    }


@router.delete("/membership-statuses/{status_id}")
def delete_membership_status(status_id: int):
    """Endpoint para eliminar un estado de membresía."""

    ok = service.delete_membership_status(status_id)

    if not ok:
        raise HTTPException(
            status_code=404,
            detail="Status not found"
        )

    return {"status": "deleted"}