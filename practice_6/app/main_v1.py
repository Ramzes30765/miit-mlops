from fastapi import FastAPI
from app.api.v1 import users, items

app = FastAPI(title="Modular FastAPI Example")

app.include_router(users.router)
app.include_router(items.router)
