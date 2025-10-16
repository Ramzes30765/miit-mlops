from fastapi import APIRouter
from app.models.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["Items"])

fake_items_db = []

@router.post("/", response_model=ItemResponse)
def create_item(item: ItemCreate):
    """Создание нового предмета."""
    new_item = {
        "id": len(fake_items_db) + 1,
        "title": item.title,
        "description": item.description,
        "owner_id": item.owner_id,
    }
    fake_items_db.append(new_item)
    return new_item


@router.get("/", response_model=list[ItemResponse])
def list_items():
    """Получение списка всех предметов."""
    return fake_items_db
