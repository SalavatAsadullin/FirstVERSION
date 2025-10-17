from fastapi import FastAPI

from app.core.config import get_settings
from app.api.router import api_router

settings = get_settings()

app = FastAPI(title=settings.app_name)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
