from datetime import date
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DeliverySlot(str, Enum):
    BEFORE_15 = "before_15"
    BEFORE_21 = "before_21"


class OrderStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = "orders"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    address_id: Mapped[int] = mapped_column(ForeignKey("addresses.id"))

    bottles: Mapped[int] = mapped_column(Integer)
    exchange_bottles: Mapped[int] = mapped_column(Integer)
    total_amount: Mapped[int] = mapped_column(Integer)

    delivery_date: Mapped[date]
    delivery_slot: Mapped[str] = mapped_column(String(20))

    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.IN_PROGRESS.value, index=True)

    comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    user = relationship("User", back_populates="orders")
    address = relationship("Address", back_populates="orders")
