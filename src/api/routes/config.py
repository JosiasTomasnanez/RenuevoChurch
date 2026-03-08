from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/ministries")
def get_ministries(request: Request):
    services = request.app.state.services
    return services.config.get_all_ministries()


@router.post("/ministries")
def create_ministry(payload: dict, request: Request):
    services = request.app.state.services
    services.config.create_ministry(payload["name"])
    return {"status": "ok"}


@router.get("/cdb")
def get_cdb(request: Request):
    services = request.app.state.services
    return services.config.get_all_cdb_options()
