from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List


# ---------- ITEMS ----------

class ItemBase(BaseModel):
    """Базовые поля, общие для всех схем предмета."""
    title: str = Field(..., min_length=1, max_length=100, description="Название предмета")
    description: Optional[str] = Field(None, max_length=300, description="Описание предмета")


class ItemCreate(ItemBase):
    """Схема входных данных при создании предмета."""
    owner_id: int = Field(..., ge=1, description="ID владельца")


class ItemResponse(ItemBase):
    """Схема ответа API при запросе предмета."""
    id: int
    owner_id: int

    class Config:
        from_attributes = True


# ---------- USERS ----------

class UserBase(BaseModel):
    """Базовые поля пользователя."""
    name: str = Field(..., min_length=1, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")


class UserCreate(UserBase):
    """Схема входных данных при регистрации пользователя."""
    password: str = Field(..., min_length=6, description="Пароль пользователя")


class UserResponse(UserBase):
    """Схема ответа API: пользователь без пароля, но со списком предметов."""
    id: int
    items: List[ItemResponse] = []

    class Config:
        from_attributes = True

class TextPredictIn(BaseModel):
    """Вход для текстовой модели (LLM)."""
    prompt: str = Field(..., min_length=1, description="Текст запроса к модели")

class TextPredictOut(BaseModel):
    """Ответ текстовой модели (заглушка)."""
    reply: str = Field(..., description="Сгенерированный ответ")
    model_version: str = Field(..., description="Версия модели")
    latency_ms: float = Field(..., ge=0.0, description="Время обработки (мс)")
