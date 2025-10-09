from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...database import get_db

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("/", response_model=schemas.OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: schemas.OrderCreate, response: Response, db: Session = Depends(get_db)):
    created = crud.create_order(db=db, order=order)
    response.headers["Location"] = f"/api/v1/orders/{created.id}"
    return created


@router.get("/", response_model=List[schemas.OrderResponse])
def list_orders(
    status: Optional[str] = None,
    city: Optional[str] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
    sort: str = "created_at:desc",
    db: Session = Depends(get_db),
):
    return crud.get_orders(
        db,
        status=status,
        city=city,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
        sort=sort,
    )


@router.get("/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    record = crud.get_order(db, order_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Заказ не найден!")
    return record


@router.patch("/{order_id}", response_model=schemas.OrderResponse)
def patch_order(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    updated = crud.update_order(db, order_id, order)
    if updated is None:
        raise HTTPException(status_code=404, detail="Заказ не найден!")
    return updated


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_order(db, order_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Заказ не найден!")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
