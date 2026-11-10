from fastapi import FastAPI, Query

app = FastAPI(title="FastAPI basics", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/search")
def search_items(
    query: str,
    limit: int = Query(default=10, ge=1, le=100),
):
    return {"query": query, "limit": limit}
