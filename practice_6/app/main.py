from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
# http://127.0.0.1:8000/items/3

@app.get("/search")
async def search_items(q: str, limit: int = 10):
    return {"query": q, "limit": limit}

# # python app/main.py
# if __name__ == '__main__':
#     uvicorn.run(app, port=8000)

# uvicorn app.main:app --reload --host 127.0.0.1 --port 8000