from fastapi import FastAPI
from app.api.v2 import users, items

app = FastAPI(title="Modular FastAPI Example with Validation")

app.include_router(users.router)
app.include_router(items.router)