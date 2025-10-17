from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import asc, desc, select
from sqlalchemy.orm import Session

from . import models, schemas


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    db_order = models.Order(**order.model_dump(exclude_none=True))
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def get_orders(
    db: Session,
    *,
    status: Optional[str] = None,
    city: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:desc",
) -> list[models.Order]:
    stmt = select(models.Order)
    if status:
        stmt = stmt.where(models.Order.status == status)
    if city:
        stmt = stmt.where(models.Order.city == city)
    if created_from:
        stmt = stmt.where(models.Order.created_at >= created_from)
    if created_to:
        stmt = stmt.where(models.Order.created_at <= created_to)

    sort_field, _, sort_dir = sort.partition(":")
    if sort_field == "created_at":
        order_clause = desc(models.Order.created_at) if sort_dir == "desc" else asc(models.Order.created_at)
        stmt = stmt.order_by(order_clause)

    stmt = stmt.offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()


def get_order(db: Session, order_id: int) -> Optional[models.Order]:
    return db.get(models.Order, order_id)


def update_order(db: Session, order_id: int, order_update: schemas.OrderUpdate) -> Optional[models.Order]:
    db_order = db.get(models.Order, order_id)
    if db_order is None:
        return None
    update_data = order_update.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    db_order = db.get(models.Order, order_id)
    if db_order is None:
        return False
    db.delete(db_order)
    db.commit()
    return True



