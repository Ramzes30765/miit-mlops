from fastapi import FastAPI
from app.api.v3 import llm

app = FastAPI(title="FastAPI Example")

app.include_router(llm.router)
