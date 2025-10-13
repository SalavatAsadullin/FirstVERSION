from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.security import get_current_user
from app.models.user import User
from app.models.address import Address, CityRegion

router = APIRouter()


class AddressCreate(BaseModel):
    region: CityRegion
    city: str
    street: str
    house: str
    entrance: str | None = None
    apartment: str | None = None
    floor: str | None = None


class AddressOut(AddressCreate):
    id: int


@router.post("/", response_model=AddressOut)
async def create_address(
    payload: AddressCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AddressOut:
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
    return AddressOut(
        id=addr.id,
        region=CityRegion(addr.region),
        city=addr.city,
        street=addr.street,
        house=addr.house,
        entrance=addr.entrance,
        apartment=addr.apartment,
        floor=addr.floor,
    )


@router.get("/", response_model=list[AddressOut])
async def list_addresses(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> list[AddressOut]:
    rows = (
        db.query(Address)
        .filter(Address.user_id == user.id)
        .order_by(Address.created_at.desc())
        .all()
    )
    return [
        AddressOut(
            id=r.id,
            region=CityRegion(r.region),
            city=r.city,
            street=r.street,
            house=r.house,
            entrance=r.entrance,
            apartment=r.apartment,
            floor=r.floor,
        )
        for r in rows
    ]
