from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class OrderBase(BaseModel):
    city: str
    street: str
    apartment: Optional[str] = None
    floor: Optional[int] = None
    entrance: Optional[str] = None
    bottles: int = Field(ge=1)
    comment: Optional[str] = None
    status: Optional[str] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    city: Optional[str] = None
    street: Optional[str] = None
    apartment: Optional[str] = None
    floor: Optional[int] = None
    entrance: Optional[str] = None
    bottles: Optional[int] = Field(default=None, ge=1)
    comment: Optional[str] = None
    status: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
