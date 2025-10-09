from fastapi import FastAPI
from .database import engine
from .models import Base
from .routers import orders

# Создаем таблицы в БД
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Подключаем роутер
app.include_router(orders.router)