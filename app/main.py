from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .routers import orders as legacy_orders
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

# Временный роутер для совместимости (будет удалён позже)
app.include_router(legacy_orders.router)