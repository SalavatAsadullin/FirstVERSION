from fastapi import APIRouter

from . import auth, orders, addresses, meta

router = APIRouter()
router.include_router(meta.router, tags=["meta"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(addresses.router, prefix="/addresses", tags=["addresses"])
router.include_router(orders.router, prefix="/orders", tags=["orders"])
