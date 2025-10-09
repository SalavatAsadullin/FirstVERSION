from sqlalchemy import Column, Integer, String
from .database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String, index=True)
    street = Column(String)
    apartment = Column(String)
    floor = Column(Integer)
    entrance = Column(String)
    bottles = Column(String)
    comment = Column(String)
    status = Column(String, default="В процессе")