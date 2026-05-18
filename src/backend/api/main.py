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
    return {
        "latest_version": "2.0.0",
        "download_url": "https://cdn.discordapp.com/attachments/1506028475692351500/1506028616096678051/instalador_prueba.sh?ex=6a0cc5f2&is=6a0b7472&hm=1baa68dc81cb7c1a68a7cbbe3ab24dcc3ab726d0ef6c7eda8f96336fce6651ca&"
    }