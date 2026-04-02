import pytest
import logging
from models.base_models import RegisterUserResponse, TestUser
from enums.roles import Roles

logger = logging.getLogger(__name__)


class TestUser:
    """Тесты Users API с Pydantic моделями"""

    def test_create_user_with_model(self, test_user: TestUser, super_admin):
        """Создание пользователя с использованием Pydantic модели"""

        # Создаём пользователя (модель автоматически конвертируется в dict)
        response = super_admin.api.user.create_user(test_user)

        # Валидируем ответ через Pydantic
        created_user = RegisterUserResponse(**response.json())

        # Проверяем данные
        assert created_user.email == test_user.email
        assert created_user.fullName == test_user.fullName
        assert Roles.USER in created_user.roles

        logger.info(f" Пользователь создан: {created_user.email}")
        logger.info(f"  ID: {created_user.id}, Roles: {[r.value for r in created_user.roles]}")

    def test_get_user_by_id(self, test_user: TestUser, super_admin):
        """Получение пользователя по ID"""

        # 1. Создаём пользователя
        create_response = super_admin.api.user.create_user(test_user)
        created_user = RegisterUserResponse(**create_response.json())

        # 2. Получаем пользователя по ID
        get_response = super_admin.api.user.get_user(created_user.id)
        user_data = get_response.json()

        # 3. Валидируем ответ
        retrieved_user = RegisterUserResponse(**user_data)

        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

        logger.info(f" Пользователь получен: {retrieved_user.email}")
