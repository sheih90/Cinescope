"""Базовые модели Pydantic для проекта Cinescope"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enums.roles import Roles  # Импортируем наш Enum


class TestUser(BaseModel):
    """
    Модель для создания пользователя (запрос).

    Используется в тестах и фикстурах.
    """
    __test__ = False
    email: str
    fullName: str
    password: str
    passwordRepeat: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="passwordRepeat должен полностью совпадать с полем password"
    )
    roles: List[Roles] = [Roles.USER]
    verified: Optional[bool] = True
    banned: Optional[bool] = False


    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        """Проверяет, что passwordRepeat совпадает с password"""
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    def to_json_for_api(self) -> dict:
        """
        Конвертирует модель в dict для отправки в API.
        Исключает passwordRepeat и сериализует Enum в строки.
        """
        data = self.model_dump(mode='json', exclude={'passwordRepeat'}, exclude_unset=True)
        return data


class RegisterUserResponse(BaseModel):
    """
    Модель для валидации ответа API при регистрации пользователя.

    Автоматически проверяет:
    - Наличие всех обязательных полей
    - Формат email (regex)
    - Формат createdAt (ISO 8601)
    - Валидные значения roles (Enum)
    """
    id: str
    email: str = Field(
        pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        description="Email пользователя"
    )
    fullName: str = Field(min_length=1, max_length=100, description="Полное имя пользователя")
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str = Field(description="Дата и время создания пользователя в формате ISO 8601")

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидирует формат даты ISO 8601"""
        try:
            datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается формат ISO 8601.")
        return value