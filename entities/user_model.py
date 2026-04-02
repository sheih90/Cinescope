from pydantic import BaseModel, Field, field_validator, ValidationError, ConfigDict
from typing import List, Optional
from enums.roles import Roles


class RegisteredUser(BaseModel):
    """
    Модель данных для зарегистрированного пользователя.

    Поля соответствуют ответу API при регистрации/создании пользователя.
    """
    email: str
    fullName: str  # точный регистр как в API!
    password: str
    passwordRepeat: str  # точный регистр как в API!
    roles: List[Roles]
    verified: Optional[bool] = None
    banned: Optional[bool] = None
    model_config = ConfigDict(from_attributes=True)

    # КАСТОМНЫЕ ВАЛИДАТОРЫ

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Проверяет, что email содержит символ @"""
        if '@' not in v:
            raise ValueError('Email должен содержать символ "@"')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Проверяет, что пароль не меньше 8 символов"""
        if len(v) < 8:
            raise ValueError('Пароль должен содержать не менее 8 символов')
        return v

    @field_validator('passwordRepeat')
    @classmethod
    def validate_password_repeat(cls, v: str, info) -> str:
        """Проверяет, что passwordRepeat совпадает с password"""
        # Получаем значение password из данных
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('passwordRepeat должен совпадать с password')
        return v