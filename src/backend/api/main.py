from fastapi import FastAPI

from .routers import people_router
from .routers import config_router

app = FastAPI(
    title="Renuevo API",
    version="1.0"
)

app.include_router(people_router.router)
app.include_router(config_router.router)
