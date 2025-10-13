from enum import Enum
from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserRole(str, Enum):
    CLIENT = "client"
    OPERATOR = "operator"
    COURIER = "courier"


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(112), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.CLIENT.value, index=True)

    addresses = relationship("Address", back_populates="user")
    orders = relationship("Order", back_populates="user")
