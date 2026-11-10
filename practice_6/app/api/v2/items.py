from fastapi import APIRouter, HTTPException, status

from app.api.v2.users import fake_users_db
from app.models.schemas import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["Items"])

fake_items_db: list[dict] = []


@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(item: ItemCreate):
    """Создание нового предмета."""
    owner = next((user for user in fake_users_db if user["id"] == item.owner_id), None)
    if owner is None:
        raise HTTPException(status_code=404, detail="Owner not found")

    new_item = {
        "id": len(fake_items_db) + 1,
        "title": item.title,
        "description": item.description,
        "owner_id": item.owner_id,
    }
    fake_items_db.append(new_item)
    owner["items"].append(new_item)
    return new_item


@router.get("", response_model=list[ItemResponse])
def list_items():
    """Получение списка всех предметов."""
    return fake_items_db
