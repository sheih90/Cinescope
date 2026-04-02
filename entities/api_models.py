from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(BaseModel):
    """Модель пользователя (ответ API)"""
    id: str
    email: str
    fullName: str
    roles: List[UserRole]
    verified: bool
    banned: bool
    createdAt: datetime

    model_config = ConfigDict(use_enum_values=True)


class UserCreate(BaseModel):
    """Модель для создания пользователя (запрос)"""
    email: str
    fullName: str
    password: str
    passwordRepeat: str
    roles: List[UserRole] = [UserRole.USER]
    verified: bool = False
    banned: bool = False

    model_config = ConfigDict(use_enum_values=True)

    def model_dump(self, *args, **kwargs):
        """Переопределяем для исключения passwordRepeat"""
        data = super().model_dump(*args, **kwargs)
        data.pop('passwordRepeat', None)
        return data


class Movie(BaseModel):
    """Модель фильма (ответ API)"""
    id: int
    name: str
    price: float
    description: str
    imageUrl: str
    location: str
    published: bool
    rating: float
    genreId: int
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class MovieCreate(BaseModel):
    """Модель для создания фильма (запрос)"""
    name: str
    price: float = Field(..., ge=0, le=1000)
    description: str
    imageUrl: str
    location: str
    published: bool = True
    genreId: int

    model_config = ConfigDict(use_enum_values=True)