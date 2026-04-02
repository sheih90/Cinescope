import pytest
from constants import ADMIN_CREDENTIALS, INVALID_PASSWORD
from utils.data_generator import DataGenerator
import logging
from models.base_models import TestUser, RegisterUserResponse
from enums.roles import Roles

logger = logging.getLogger(__name__)


class TestAuth:
    """Тесты для авторизации и регистрации"""

    def test_register_user(self, api_manager, test_user: TestUser):
        """Регистрация нового пользователя с валидацией ответа через Pydantic"""

        # Отправляем запрос
        response = api_manager.auth.register_user(user_data=test_user)

        # Валидируем ответ через Pydantic модель
        register_user_response = RegisterUserResponse(**response.json())

        # Проверяем только то, что мы контролируем:
        assert register_user_response.email == test_user.email, "Email не совпадает"
        assert register_user_response.fullName == test_user.fullName, "Имя не совпадает"

        # Проверяем, что роли корректны (но не сравниваем с входными, т.к. могут быть дефолты)
        assert Roles.USER in register_user_response.roles, "Роль USER должна быть"

        # Проверяем, что обязательные поля есть и имеют правильный тип
        assert isinstance(register_user_response.verified, bool), "verified должен быть bool"
        assert isinstance(register_user_response.banned, bool), "banned должен быть bool"
        assert isinstance(register_user_response.id, str), "id должен быть строкой"
        assert isinstance(register_user_response.createdAt, str), "createdAt должен быть строкой"

        # Логируем
        logger.info(f"✓ Пользователь зарегистрирован: {register_user_response.email}")
        logger.info(f"  ID: {register_user_response.id}, verified: {register_user_response.verified}")

    def test_register_and_login_user(self, api_manager, test_user: TestUser):
        """Тест на регистрацию и авторизацию пользователя"""

        # Регистрируем (модель автоматически сериализуется)
        register_response = api_manager.auth.register_user(test_user)
        registered = RegisterUserResponse(**register_response.json())

        # Валидируем через модель
        assert registered.email == test_user.email

        # Логинимся
        login_data = {
            "email": test_user.email,
            "password": test_user.password
        }
        login_response = api_manager.auth.login_user(login_data)
        login_data_response = login_response.json()

        assert "accessToken" in login_data_response
        assert login_data_response["user"]["email"] == test_user.email

        logger.info(f"Регистрация + логин: {registered.email}")

    def test_register_not_email(self, api_manager, random_user):
        """Тест регистрации без почты"""
        user = random_user.copy()
        user["email"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Bad Request"

    def test_register_not_full_name(self, api_manager, random_user):
        """Тест регистрации без имени"""
        user = random_user.copy()
        user["fullName"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Bad Request"

    def test_register_not_password(self, api_manager, random_user):
        """Тест регистрации без пароля"""
        user = random_user.copy()
        user["password"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Bad Request"

    def test_register_not_password_repeat(self, api_manager, random_user):
        """Тест регистрации без подтверждения пароля"""
        user = random_user.copy()
        user["passwordRepeat"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Bad Request"

    def test_register_repeat_email(self, api_manager, random_user):
        """Регистрация пользователя с существующим email"""

        # 1. Первый запрос — успех
        register_response = api_manager.auth.register_user(random_user)
        assert "id" in register_response.json()

        # 2. Второй запрос — конфликт (тот же email)
        conflict_response = api_manager.auth.register_user(random_user, expected_status=409)
        assert conflict_response.json()["error"] == "Conflict"

    def test_login_success(self, api_manager):
        """Тест успешного логина админа"""
        response = api_manager.auth.login_user(ADMIN_CREDENTIALS)
        data = response.json()

        assert "accessToken" in data
        assert "expiresIn" in data
        assert "user" in data
        assert data["accessToken"] != ""

        user = data["user"]
        assert "id" in user
        assert "email" in user
        assert "fullName" in user
        assert "roles" in user
        assert user["email"] == ADMIN_CREDENTIALS["email"]

    def test_login_invalid_password(self, api_manager):
        """Тест логина с неправильным паролем"""
        invalid_credentials = {
            "email": ADMIN_CREDENTIALS["email"],
            "password": INVALID_PASSWORD
        }
        response = api_manager.auth.login_user(invalid_credentials, expected_status=401)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Unauthorized"

    def test_login_empty_body(self, api_manager):
        """Тест логина с пустым телом запроса"""
        response = api_manager.auth.login_user({}, expected_status=401)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Unauthorized"

    def test_create_user(self, api_manager_auth, test_user: TestUser):
        """Тест создания пользователя супер-админом"""

        response = api_manager_auth.user.create_user(test_user)
        created = RegisterUserResponse(**response.json())

        # Валидируем через модель
        assert created.email == test_user.email
        assert created.fullName == test_user.fullName
        assert isinstance(created.verified, bool)
        assert isinstance(created.banned, bool)

        logger.info(f"Пользователь создан: {created.email}")

    def test_create_user_without_auth(self, api_manager, test_user: TestUser):
        """Тест создания пользователя без авторизации"""
        response = api_manager.user.create_user(test_user, expected_status=401)
        data = response.json()
        assert data["message"] == "Unauthorized"

    def test_create_user_with_existing_email(self, api_manager_auth, test_user: TestUser):
        """Тест создания пользователя с существующим email"""

        # 1. Первый запрос — успех
        create_response = api_manager_auth.user.create_user(test_user)
        created = RegisterUserResponse(**create_response.json())
        assert created.email == test_user.email

        # 2. Второй запрос — конфликт (тот же email)
        conflict_response = api_manager_auth.user.create_user(test_user, expected_status=409)
        data = conflict_response.json()
        assert data["error"] == "Conflict"

    def test_update_user_verified(self, api_manager_auth, random_user_data):
        """Тест обновления verified у пользователя"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        user_id = create_response.json()["id"]

        # 2. Обновляем verified
        update_data = {
            "verified": not random_user_data["verified"],
            "banned": random_user_data["banned"]
        }
        update_response = api_manager_auth.user.update_user(user_id, update_data)

        updated_data = update_response.json()
        assert updated_data["verified"] == update_data["verified"]

    def test_update_user_banned(self, api_manager_auth, random_user_data):
        """Тест обновления banned у пользователя"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        user_id = create_response.json()["id"]

        # 2. Обновляем banned
        update_data = {
            "banned": not random_user_data["banned"],
            "verified": random_user_data["verified"]
        }
        update_response = api_manager_auth.user.update_user(user_id, update_data)

        updated_data = update_response.json()
        assert updated_data["banned"] == update_data["banned"]

    def test_add_user_to_admin(self, api_manager_auth, random_user_data):
        """Тест добавления дополнительной роли ADMIN"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        created_user = create_response.json()
        user_id = created_user["id"]
        assert created_user["roles"] == ["USER"]

        # 2. Повышаем до ADMIN
        update_data = {
            "roles": ["USER", "ADMIN"],
            "verified": random_user_data["verified"],
            "banned": random_user_data["banned"]
        }
        update_response = api_manager_auth.user.update_user(user_id, update_data)

        updated_user = update_response.json()
        assert updated_user["roles"] == update_data["roles"]

    def test_update_user_invalid_verified(self, api_manager_auth, random_user_data):
        """Тест обновления пользователя с некорректным verified"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        user_id = create_response.json()["id"]

        # 2. Некорректное значение для verified
        update_data = {
            "verified": 123,  # Должно быть boolean
            "banned": random_user_data["banned"]
        }
        response = api_manager_auth.user.update_user(user_id, update_data, expected_status=400)

        data = response.json()
        assert data["error"] == "Bad Request"
        assert "message" in data

    def test_update_user_invalid_banned(self, api_manager_auth, random_user_data):
        """Тест обновления пользователя с некорректным banned"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        user_id = create_response.json()["id"]

        # 2. Некорректное значение для banned
        update_data = {
            "verified": random_user_data["verified"],
            "banned": "asd"  # Должно быть boolean
        }
        response = api_manager_auth.user.update_user(user_id, update_data, expected_status=400)

        data = response.json()
        assert data["error"] == "Bad Request"
        assert "message" in data

    def test_promote_user_to_invalid_role(self, api_manager_auth, random_user_data):
        """Тест изменения пользователя на некорректную роль"""

        # 1. Создаём пользователя
        create_response = api_manager_auth.user.create_user(random_user_data)
        user_id = create_response.json()["id"]
        assert create_response.json()["roles"] == ["USER"]

        # 2. Некорректная роль (нижний регистр)
        update_data = {
            "roles": "admin",  # Должно быть ["ADMIN"]
            "verified": random_user_data["verified"],
            "banned": random_user_data["banned"]
        }
        response = api_manager_auth.user.update_user(user_id, update_data, expected_status=400)

        data = response.json()
        assert data["error"] == "Bad Request"
        assert "message" in data