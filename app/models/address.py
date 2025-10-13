from typing import Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Address(Base):
    __tablename__ = "addresses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    region: Mapped[str] = mapped_column(String(50))  # city or mirny
    city: Mapped[str] = mapped_column(String(120))
    street: Mapped[str] = mapped_column(String(200))
    house: Mapped[str] = mapped_column(String(50))
    entrance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    apartment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    floor: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    user = relationship("User", back_populates="addresses")
    orders = relationship("Order", back_populates="address")
