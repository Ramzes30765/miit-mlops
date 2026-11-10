from fastapi import FastAPI

from app.api.v2 import users, items

app = FastAPI(title="FastAPI validation", version="2.0.0")

app.include_router(users.router, prefix="/api/v2")
app.include_router(items.router, prefix="/api/v2")
