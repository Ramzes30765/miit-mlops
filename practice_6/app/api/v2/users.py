from fastapi import APIRouter
from app.models.schemas import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

fake_users_db = []  # временное хранилище

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    """Создание нового пользователя."""
    new_user = {
        "id": len(fake_users_db) + 1,
        "name": user.name,
        "email": user.email,
        "items": []
    }
    fake_users_db.append(new_user)
    return new_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    """Получение пользователя по ID."""
    for u in fake_users_db:
        if u["id"] == user_id:
            return u
    return {"error": "User not found"}
