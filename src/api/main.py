from fastapi import FastAPI
from src.backend.app.main import create_app

from .routes.people import router as people_router
from .routes.config import router as config_router

backend_app = create_app()

app = FastAPI(title="Renuevo API")

app.state.services = backend_app.services

app.include_router(people_router, prefix="/people")
app.include_router(config_router, prefix="/config")
