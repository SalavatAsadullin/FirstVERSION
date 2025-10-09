from sqlalchemy.orm import Session
from . import models, schemas

def create_order(db: Session, order: schemas.OrderCreate):
    db_order = models.Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
def get_orders(db:Session):
    return db.query(models.Order).all()
def get_order(db:Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first() # type: ignore

def update_order(db:Session, order_id: int, order_update: schemas.OrderUpdate):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)
    db.commit()
    db.refresh(db_order)
    return db_order

def delete_order(db:Session, order_id: int):
    db_order = get_order(db, order_id)
    if db_order is None:
        return None
    db.delete(db_order)
    db.commit()
    return {"message": f"Заказ с ID: {order_id} удалён"}



