import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware 
from src.backend.app.main import create_app
from .routers import people_router, config_router

app = FastAPI(
    title="Renuevo API",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
)

container = create_app()

app.include_router(people_router.router)
app.include_router(config_router.router)

@app.get("/api/version")
def get_software_version():
    latest = os.environ.get("LATEST_VERSION", "1.0.0")
    download = os.environ.get("DOWNLOAD_URL", "")

    return {
        "latest_version": latest,
        "download_url": download
    }

@app.get("/api/version-mobile")
def get_mobile_software_version():
    latest_mobile = os.environ.get("MOBILE_LATEST_VERSION", "1.0.0")
    download_mobile = os.environ.get("MOBILE_DOWNLOAD_URL", "")
    
    return {
        "latest_version": latest_mobile,
        "download_url": download_mobile
    }
