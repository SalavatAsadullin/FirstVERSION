from datetime import date
from enum import Enum
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.config import get_settings

router = APIRouter()


class DeliverySlot(str, Enum):
    BEFORE_15 = "before_15"
    BEFORE_21 = "before_21"


class OrderStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class CityRegion(str, Enum):
    CITY = "city"
    MIRNY = "mirny"


class OrderCreate(BaseModel):
    bottles: int = Field(ge=0)
    exchange_bottles: int = Field(ge=0)
    delivery_date: date
    delivery_slot: DeliverySlot
    region: CityRegion
    city: str
    street: str
    house: str
    entrance: Optional[str] = None
    apartment: Optional[str] = None
    floor: Optional[str] = None
    phone: str = Field(min_length=1, max_length=112)
    comment: Optional[str] = None


class OrderOut(BaseModel):
    id: int
    total_amount: int
    status: OrderStatus


@router.post("/", response_model=OrderOut)
async def create_order(payload: OrderCreate) -> OrderOut:
    settings = get_settings()
    price_per = settings.price_per_bottle
    total = (payload.bottles - payload.exchange_bottles) * price_per
    if total < 0:
        total = 0
    # TODO: persist to DB
    return OrderOut(id=1, total_amount=total, status=OrderStatus.IN_PROGRESS)


class OrderRow(BaseModel):
    id: int
    bottles: int
    exchange_bottles: int
    total_amount: int
    status: OrderStatus


@router.get("/", response_model=list[OrderRow])
async def list_orders() -> list[OrderRow]:
    # TODO: read from DB; filtering by region tabs
    return []


@router.post("/{order_id}/take", response_model=OrderOut)
async def take_order(order_id: int) -> OrderOut:
    # TODO: role check (courier/operator), update status
    return OrderOut(id=order_id, total_amount=0, status=OrderStatus.IN_PROGRESS)
