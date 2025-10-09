from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .api.v1.orders import router as v1_orders


settings = get_settings()

app = FastAPI(title=settings.app_name)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok"}


# Новый роутер API v1
app.include_router(v1_orders)

# Автоматическая инициализация схемы БД в dev окружении
if settings.environment == "development":
    from .database import Base, engine  # noqa: WPS433 (import within scope)
    from . import models  # noqa: F401 — register models

    Base.metadata.create_all(bind=engine)