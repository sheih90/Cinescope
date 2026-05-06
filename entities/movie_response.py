from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class GenreResponse(BaseModel):
    """Модель жанра в ответе API"""
    name: str


class MovieResponse(BaseModel):
    """
    Pydantic модель для валидации ответа API о фильме.

    Все поля сделаны гибкими, так как API может возвращать
    разные структуры в зависимости от контекста.
    """
    id: int
    name: str
    price: int
    description: Optional[str] = None  # ← Может быть null
    imageUrl: Optional[str] = None  # ← Может быть null!
    location: str
    published: bool
    rating: Optional[float] = 0.0  # ← Может отсутствовать
    genreId: int
    createdAt: datetime
    reviews: Optional[List[Any]] = []  # ← Может отсутствовать
    genre: Optional[GenreResponse] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra='ignore'  # Игнорируем лишние поля из API
    )