from fastapi import APIRouter

router = APIRouter(prefix="/items", tags=["Items"])

@router.get("/")
def list_items():
    return [{"id": 1, "title": "Book"}]
