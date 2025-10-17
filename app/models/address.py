from typing import Optional
from enum import Enum

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CityRegion(str, Enum):
    CITY = "city"
    MIRNY = "mirny"


class Address(Base):
    __tablename__ = "addresses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    region: Mapped[str] = mapped_column(String(50))  # values from CityRegion
    city: Mapped[str] = mapped_column(String(120))
    street: Mapped[str] = mapped_column(String(200))
    house: Mapped[str] = mapped_column(String(50))
    entrance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    apartment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")
