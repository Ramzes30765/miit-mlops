from fastapi import FastAPI

from app.api.v3 import llm

app = FastAPI(title="Text API contract demo", version="3.0.0")

app.include_router(llm.router, prefix="/api/v3")


@app.get("/health", tags=["Service"])
def health():
    return {"status": "ok", "model_version": "demo-llm-v1"}
