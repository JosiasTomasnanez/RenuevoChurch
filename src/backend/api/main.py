import os
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

@app.get("/api/version")
def get_software_version():
    # Render va a mandar estos valores dinámicamente
    latest = os.environ.get("LATEST_VERSION", "1.0.0")
    download = os.environ.get("DOWNLOAD_URL", "")

    return {
        "latest_version": latest,
        "download_url": download
    }