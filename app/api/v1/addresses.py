from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AddressCreate(BaseModel):
    region: str
    city: str
    street: str
    house: str
    entrance: str | None = None
    apartment: str | None = None
    floor: str | None = None


class AddressOut(AddressCreate):
    id: int


@router.post("/", response_model=AddressOut)
async def create_address(payload: AddressCreate) -> AddressOut:
    # TODO: persist address for current user
    return AddressOut(id=1, **payload.model_dump())


@router.get("/", response_model=list[AddressOut])
async def list_addresses() -> list[AddressOut]:
    # TODO: fetch addresses for current user
    return []
