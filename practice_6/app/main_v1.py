from fastapi import FastAPI

from app.api.v1 import users, items

app = FastAPI(title="FastAPI routers", version="1.0.0")

app.include_router(users.router, prefix="/api/v1")
app.include_router(items.router, prefix="/api/v1")
