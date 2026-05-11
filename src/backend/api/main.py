from fastapi import FastAPI

from src.backend.app.main import create_app

from .routers import people_router, config_router

app = FastAPI(
    title="Renuevo API",
    version="1.0"
)

container = create_app()

app.include_router(people_router.router)
app.include_router(config_router.router)
