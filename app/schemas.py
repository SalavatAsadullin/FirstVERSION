from pydantic import BaseModel

class OrderCreate(BaseModel):
    city: str
    street: str
    apartment: str
    floor: int
    entrance: str
    bottles: int
    comment: str
    status: str

class OrderUpdate(BaseModel):
    city: str | None = None
    street: str | None = None
    apartment: str | None = None
    floor: int | None = None
    entrance: str | None = None
    bottles: int | None = None
    comment: str | None = None
    status: str | None = None

class Order(OrderCreate):
    id: int


