import pytest
import requests
from constants import BASE_AUTH_URL, HEADERS, ADMIN_CREDENTIALS, LOGIN_ENDPOINT, USER_ENDPOINT, REGISTER_ENDPOINT


class TestAuth:
    """Тесты для POST /auth/register/user"""

    def test_register_user(self, requester, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_success(self, api_manager, random_user):
        """Тест успешной регистрации через ApiManager"""
        response = api_manager.auth.register_user(random_user)
        data = response.json()
        assert data["email"] == random_user["email"]
        assert "id" in data
        assert "roles" in data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in data["roles"], "Роль USER должна быть у пользователя"


    def test_register_and_login_user(self, api_manager, random_user):
        """Тест на регистрацию и авторизацию пользователя"""

        # 1. Регистрируем пользователя
        register_response = api_manager.auth.register_user(random_user)
        assert register_response.json()["email"] == random_user["email"]

        # 2. Логинимся
        login_data = {
            "email": random_user["email"],
            "password": random_user["password"]
        }
        login_response = api_manager.auth.login_user(login_data)

        response_data = login_response.json()
        assert "accessToken" in response_data
        assert response_data["user"]["email"] == random_user["email"]


    def test_register_not_email(self, api_manager, random_user):
        """Тест регистрации без почты"""
        user = random_user.copy()
        user["email"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        response_data = response.json()
        assert "message" in response_data
        assert response_data["error"] == "Bad Request"


    def test_register_not_full_name(self, api_manager, random_user):
        """Тест регистрации без имени"""
        user = random_user.copy()
        user["fullName"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        response_data = response.json()
        assert "message" in response_data
        assert response_data["error"] == "Bad Request"


    def test_register_not_password(self, api_manager, random_user):
        """Тест регистрации без пароля"""
        user = random_user.copy()
        user["password"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        response_data = response.json()
        assert "message" in response_data
        assert response_data["error"] == "Bad Request"

    def test_register_not_password_repeat(self, api_manager, random_user):
        """Тест регистрации без подтверждения пароля"""
        user = random_user.copy()
        user["passwordRepeat"] = ""
        response = api_manager.auth.register_user(user, expected_status=400)
        response_data = response.json()
        assert "message" in response_data
        assert response_data["error"] == "Bad Request"

    def test_register_repeat_email(self, api_manager, random_user):
        """Регистрация пользователя с существующим email"""
        user = {
            "email": random_user["email"],
            "fullName": "Пользователь Тестович",
            "password": "Test7241@",
            "passwordRepeat": "Test7241@"
        }

        # Первый запрос — успех
        register_response = api_manager.auth.register_user(user)
        assert "id" in register_response.json()

        # Второй запрос — конфликт
        conflict_response = api_manager.auth.register_user(user, expected_status=409)
        assert conflict_response.json()["error"] == "Conflict"


    def test_login_success(self, api_manager):
        """Тест успешного логина"""
        response = api_manager.auth.login_user(ADMIN_CREDENTIALS)
        data = response.json()
        assert "accessToken" in data
        assert "expiresIn" in data
        assert "user" in data
        # Проверяем что токены не пустые
        assert data["accessToken"] != ""
        # Проверяем структуру user
        user = data["user"]
        assert "id" in user
        assert "email" in user
        assert "fullName" in user
        assert "roles" in user
        assert user["email"] == ADMIN_CREDENTIALS["email"]


    def test_login_invalid_password(self, api_manager):
        """Тест логина с неправильным паролем"""
        user = {
            "email": "api1@gmail.com",
            "password": "asdqwe123"
        }
        response = api_manager.auth.login_user(user, expected_status=401)
        data = response.json()
        assert "message" in data
        assert data["error"] == "Unauthorized"

    def test_login_empty_body(self, api_manager):
        """Тест логина с пустым телом запроса"""
        user = {}
        response = api_manager.auth.login_user(user, expected_status=401)
        assert response.status_code == 401
        data = response.json()
        assert "message" in data
        assert data["error"] == "Unauthorized"


    def test_create_user(self, api_manager_auth, random_user_data):
        """Тест создания пользователя супер-админом"""
        response = api_manager_auth.user.create_user(random_user_data)

        data = response.json()

        # Проверяем что пользователь создан
        assert "id" in data
        assert data["email"] == random_user_data["email"]
        assert data["fullName"] == random_user_data["fullName"]
        assert "verified" in data
        assert "roles" in data
        assert "createdAt" in data


    def test_create_user_without_auth(self, api_manager, random_user_data):
        """Тест создания пользователя без авторизации"""
        response = api_manager.user.create_user(random_user_data, expected_status=401
        )
        data = response.json()
        assert data["message"] == "Unauthorized"

    def test_create_user_with_existing_email(self, api_manager_auth, random_user_data):
        """Тест создания пользователя с существующим email"""
        # Первый запрос — успех (201)
        response_create = api_manager_auth.user.create_user(random_user_data)

        created_user = response_create.json()
        assert "id" in created_user
        assert created_user["email"] == random_user_data["email"]

        # Второй запрос — конфликт (409)
        response = api_manager_auth.user.create_user(random_user_data,expected_status=409)

        data = response.json()
        assert data["message"] == "Пользователь с таким email уже зарегистрирован"
        assert data["error"] == "Conflict"

    # def test_update_user_verified(self, api_requester, random_user_data):
    #     """Тест обновления verified у пользователя"""
    #     # Создаём пользователя
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     data = response_create.json()
    #     user_id = data["id"]
    #
    #     # Инвертируем verified
    #     new_verified_value = not random_user_data["verified"]
    #
    #     # Данные для обновления
    #     update_user = {
    #         "verified": new_verified_value,
    #         "banned": random_user_data["banned"]
    #     }
    #
    #     # Обновляем пользователя
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{user_id}",
    #         data=update_user,
    #         expected_status=200
    #     )
    #
    #     updated_data = response_update.json()
    #     assert updated_data["verified"] == new_verified_value
    #
    # def test_update_user_banned(self, api_requester, random_user_data):
    #     """Тест обновления banned у пользователя"""
    #     # Создаём пользователя
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     data = response_create.json()
    #     user_id = data["id"]
    #
    #     # Инвертируем banned
    #     new_verified_banned = not random_user_data["banned"]
    #
    #     # Данные для обновления
    #     update_user = {
    #         "banned": new_verified_banned,
    #         "verified": random_user_data["verified"]
    #     }
    #     # Обновляем пользователя
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{user_id}",
    #         data=update_user,
    #         expected_status=200
    #     )
    #
    #     updated_data = response_update.json()
    #     assert updated_data["banned"] == new_verified_banned
    #
    # def test_add_user_to_admin(self, api_requester, random_user_data, user_roles):
    #     """Тест добавления дополнительной роли ADMIN"""
    #     # Создаём пользователя
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     created_user = response_create.json()
    #     created_user_id = created_user["id"]
    #     assert created_user["roles"] == ["USER"]
    #
    #     # Повышаем до ADMIN
    #     update_data = {
    #         "roles": user_roles["ADMIN"],
    #         "verified": random_user_data["verified"],
    #         "banned": random_user_data["banned"]
    #     }
    #
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{created_user_id}",
    #         data=update_data,
    #         expected_status=200
    #     )
    #
    #     update_user = response_update.json()
    #     assert update_user["roles"] == update_data["roles"]
    #
    #
    # def test_update_user_invalid_verified(self, api_requester, random_user_data):
    #     """Тест обновления пользователя с некорректным verified"""
    #     # Создаём пользователя
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     data = response_create.json()
    #     user_id = data["id"]
    #
    #     # Некорректное значение для verified
    #     invalid_verified_value = 123
    #
    #     # Данные для обновления
    #     update_user = {
    #         "verified": invalid_verified_value,
    #         "banned": random_user_data["banned"]
    #     }
    #
    #     # Обновляем пользователя (ожидаем 400)
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{user_id}",
    #         data=update_user,
    #         expected_status=400
    #     )
    #
    #     updated_data = response_update.json()
    #     assert updated_data["error"] == "Bad Request"
    #     assert "message" in updated_data
    #
    # def test_update_user_invalid_banned(self, api_requester, random_user_data):
    #     """Тест обновления пользователя с некорректным banned"""
    #     # Создаём пользователя
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     data = response_create.json()
    #     user_id = data["id"]
    #
    #     # Некорректное значение для banned
    #     invalid_verified_banned = "asd"
    #
    #     # Данные для обновления
    #     update_user = {
    #         "verified": random_user_data["verified"],
    #         "banned": invalid_verified_banned
    #     }
    #
    #     # Обновляем пользователя (ожидаем 400)
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{user_id}",
    #         data=update_user,
    #         expected_status=400
    #     )
    #
    #     updated_data = response_update.json()
    #     assert updated_data["error"] == "Bad Request"
    #     assert "message" in updated_data
    #
    # def test_promote_user_to_invalid_role(self, api_requester, random_user_data, user_roles):
    #     """Тест изменения пользователя на некорректную роль"""
    #     response_create = api_requester.send_request(
    #         method="POST",
    #         endpoint=USER_ENDPOINT,
    #         data=random_user_data,
    #         expected_status=201
    #     )
    #     assert response_create.status_code == 201
    #     created_user = response_create.json()
    #     user_id = created_user["id"]
    #
    #     assert created_user["roles"] == ["USER"]
    #
    #     update_data = {
    #         "roles": "admin",
    #         "verified": random_user_data["verified"],
    #         "banned": random_user_data["banned"]
    #     }
    #
    #     response_update = api_requester.send_request(
    #         method="PATCH",
    #         endpoint=f"{USER_ENDPOINT}/{user_id}",
    #         data=update_data,
    #         expected_status=400
    #     )
    #
    #     assert response_update.status_code == 400
    #     updated_data = response_update.json()
    #     assert updated_data["error"] == "Bad Request"
    #     assert "message" in updated_data



