from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.security import get_current_user, require_roles
from app.models.user import User, UserRole
from app.models.order import Order, OrderStatus, DeliverySlot
from app.models.address import Address, CityRegion
from app.services.pricing import calculate_total_amount

router = APIRouter()


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
async def create_order(
    payload: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> OrderOut:
    total = calculate_total_amount(payload.bottles, payload.exchange_bottles)

    # Find or create address for user (exact match by fields)
    addr = (
        db.query(Address)
        .filter(
            Address.user_id == user.id,
            Address.region == payload.region.value,
            Address.city == payload.city,
            Address.street == payload.street,
            Address.house == payload.house,
            Address.entrance == payload.entrance,
            Address.apartment == payload.apartment,
            Address.floor == payload.floor,
        )
        .one_or_none()
    )
    if addr is None:
        addr = Address(
            user_id=user.id,
            region=payload.region.value,
            city=payload.city,
            street=payload.street,
            house=payload.house,
            entrance=payload.entrance,
            apartment=payload.apartment,
            floor=payload.floor,
        )
        db.add(addr)
        db.commit()
        db.refresh(addr)

    order = Order(
        user_id=user.id,
        address_id=addr.id,
        bottles=payload.bottles,
        exchange_bottles=payload.exchange_bottles,
        total_amount=total,
        delivery_date=payload.delivery_date,
        delivery_slot=payload.delivery_slot.value,
        contact_phone=payload.phone,
        comment=payload.comment,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderOut(id=order.id, total_amount=order.total_amount, status=OrderStatus(order.status))


class OrderRow(BaseModel):
    id: int
    bottles: int
    exchange_bottles: int
    total_amount: int
    status: OrderStatus
    courier_id: int | None = None


@router.get("/", response_model=list[OrderRow])
async def list_orders(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OPERATOR.value, UserRole.COURIER.value)),
    region: CityRegion | None = None,
) -> list[OrderRow]:
    q = db.query(Order)
    if region is not None:
        q = q.join(Address).filter(Address.region == region.value)
    q = q.order_by(Order.created_at.desc())
    rows = q.all()
    return [
        OrderRow(
            id=o.id,
            bottles=o.bottles,
            exchange_bottles=o.exchange_bottles,
            total_amount=o.total_amount,
            status=OrderStatus(o.status),
            courier_id=o.courier_id,
        )
        for o in rows
    ]


@router.get("/my", response_model=list[OrderRow])
async def list_my_orders(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[OrderRow]:
    rows = (
        db.query(Order)
        .filter(Order.user_id == user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return [
        OrderRow(
            id=o.id,
            bottles=o.bottles,
            exchange_bottles=o.exchange_bottles,
            total_amount=o.total_amount,
            status=OrderStatus(o.status),
            courier_id=o.courier_id,
        )
        for o in rows
    ]


@router.post("/{order_id}/take", response_model=OrderOut)
async def take_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.COURIER.value, UserRole.OPERATOR.value)),
) -> OrderOut:
    order = db.query(Order).filter(Order.id == order_id).one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    # Assign courier if courier role
    if user.role == UserRole.COURIER.value:
        order.courier_id = user.id
    order.status = OrderStatus.IN_PROGRESS.value
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderOut(id=order.id, total_amount=order.total_amount, status=OrderStatus(order.status))


class OrderUpdateStatus(BaseModel):
    status: OrderStatus


@router.post("/{order_id}/status", response_model=OrderOut)
async def set_status(
    order_id: int,
    payload: OrderUpdateStatus,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.COURIER.value, UserRole.OPERATOR.value)),
) -> OrderOut:
    order = db.query(Order).filter(Order.id == order_id).one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    # Only courier assigned or operators can change
    if user.role == UserRole.COURIER.value and order.courier_id not in (None, user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not assigned")
    order.status = payload.status.value
    db.add(order)
    db.commit()
    db.refresh(order)
    return OrderOut(id=order.id, total_amount=order.total_amount, status=OrderStatus(order.status))


@router.get("/cities", response_model=list[str])
async def list_cities_by_region(
    region: CityRegion,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.OPERATOR.value, UserRole.COURIER.value)),
) -> list[str]:
    # Unique cities where there are orders in the given region
    q = (
        db.query(Address.city)
        .join(Order, Order.address_id == Address.id)
        .filter(Address.region == region.value)
        .distinct()
        .order_by(Address.city.asc())
    )
    return [row[0] for row in q.all()]
