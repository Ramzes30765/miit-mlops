from pydantic import BaseModel, EmailStr, Field


# ---------- ITEMS ----------


class ItemBase(BaseModel):
    """Базовые поля, общие для всех схем предмета."""
    title: str = Field(min_length=1, max_length=100, description="Название предмета")
    description: str | None = Field(default=None, max_length=300, description="Описание предмета")


class ItemCreate(ItemBase):
    """Схема входных данных при создании предмета."""
    owner_id: int = Field(ge=1, description="ID владельца")


class ItemResponse(ItemBase):
    """Схема ответа API при запросе предмета."""
    id: int
    owner_id: int


# ---------- USERS ----------


class UserBase(BaseModel):
    """Базовые поля пользователя."""
    name: str = Field(min_length=1, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(description="Email пользователя")


class UserCreate(UserBase):
    """Схема входных данных при регистрации пользователя."""
    password: str = Field(min_length=6, max_length=128, description="Пароль пользователя")


class UserResponse(UserBase):
    """Схема ответа API: пользователь без пароля, но со списком предметов."""
    id: int
    items: list[ItemResponse] = Field(default_factory=list)


class TextPredictIn(BaseModel):
    """Входные данные демонстрационного текстового endpoint."""
    prompt: str = Field(min_length=1, description="Текст запроса")


class TextPredictOut(BaseModel):
    """Ответ демонстрационного текстового endpoint."""
    reply: str = Field(description="Демонстрационный текст ответа")
    model_version: str = Field(description="Условная версия модели")
    latency_ms: float = Field(ge=0.0, description="Время выполнения заглушки в мс")
