import pytest
import logging
from entities.user_model import RegisteredUser
from models.base_models import TestUser  # ← Добавь этот импорт!
from enums.roles import Roles
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def test_registered_user_model(registration_user_data):
    """Тест: модель правильно валидирует данные пользователя"""

    # Создаём объект модели
    user = RegisteredUser(**registration_user_data)

    # Проверяем поля
    assert user.email == registration_user_data["email"]
    assert user.fullName == registration_user_data["fullName"]
    assert user.password == registration_user_data["password"]
    assert user.passwordRepeat == registration_user_data["passwordRepeat"]
    assert [role.value for role in user.roles] == registration_user_data["roles"]

    # Проверяем типы
    assert isinstance(user.email, str)
    assert isinstance(user.fullName, str)
    assert isinstance(user.password, str)
    assert isinstance(user.roles, list)

    logger.info(f"Создан пользователь: email={user.email}, fullName={user.fullName}, roles={user.roles}")


def test_validate_test_user_fixture(test_user: TestUser):
    """Тест: валидация фикстуры test_user"""
    logger.info(f"test_user data: {test_user}")

    # Конвертируем модель в dict перед распаковкой
    user = RegisteredUser(**test_user.model_dump())

    # Доступ к полям модели через атрибуты, не как к dict!
    assert user.email == test_user.email
    assert user.fullName == test_user.fullName
    assert user.password == test_user.password
    assert user.passwordRepeat == test_user.passwordRepeat

    # Проверяем, что roles — это список Roles
    assert isinstance(user.roles, list)
    assert all(isinstance(role, Roles) for role in user.roles)

    # Логируем
    logger.info(f"✓ test_user валидирован: email={user.email}, roles={user.roles}")


def test_validate_creation_user_fixture(creation_user_data):
    """Тест: валидация фикстуры creation_user_data"""
    logger.info(f"creation_user_data: {creation_user_data}")

    # creation_user_data — это dict, используем его напрямую
    user = RegisteredUser(**creation_user_data)

    # creation_user_data — dict, доступ через ["key"]
    assert user.email == creation_user_data["email"]
    assert user.fullName == creation_user_data["fullName"]
    assert user.password == creation_user_data["password"]
    assert user.passwordRepeat == creation_user_data["passwordRepeat"]

    # Проверяем roles
    assert isinstance(user.roles, list)
    assert all(isinstance(role, Roles) for role in user.roles)

    # Проверяем опциональные поля
    assert user.verified == creation_user_data.get("verified")
    assert user.banned == creation_user_data.get("banned")

    # Логируем
    logger.info(f"creation_user_data валидирован: email={user.email}, "
                f"verified={user.verified}, banned={user.banned}")


def test_convert_to_json_with_exclude_unset(test_user: TestUser, creation_user_data):
    """
    Тест: конвертация в JSON с exclude_unset=True и без.
    """
    logger.info("=" * 80)
    logger.info("Задание 4: Конвертация в JSON")
    logger.info("=" * 80)

    # Создаём объекты: test_user — модель, creation_user_data — dict
    user_from_test = RegisteredUser(**test_user.model_dump())
    user_from_creation = RegisteredUser(**creation_user_data)

    # 1. test_user с exclude_unset=True
    json_test_user_exclude = user_from_test.model_dump_json(exclude_unset=True)
    logger.info("\n test_user с exclude_unset=True:")
    logger.info(json_test_user_exclude)
    logger.info(f"Длина: {len(json_test_user_exclude)} символов")

    # 2. test_user БЕЗ exclude_unset
    json_test_user_full = user_from_test.model_dump_json()
    logger.info("\n test_user БЕЗ exclude_unset:")
    logger.info(json_test_user_full)
    logger.info(f"Длина: {len(json_test_user_full)} символов")

    # 3. creation_user_data с exclude_unset=True
    json_creation_exclude = user_from_creation.model_dump_json(exclude_unset=True)
    logger.info("\n creation_user_data с exclude_unset=True:")
    logger.info(json_creation_exclude)
    logger.info(f"Длина: {len(json_creation_exclude)} символов")

    # 4. creation_user_data БЕЗ exclude_unset
    json_creation_full = user_from_creation.model_dump_json()
    logger.info("\n creation_user_data БЕЗ exclude_unset:")
    logger.info(json_creation_full)
    logger.info(f"Длина: {len(json_creation_full)} символов")

    # Анализируем разницу
    logger.info("\n" + "=" * 80)
    logger.info(" АНАЛИЗ РАЗНИЦЫ:")
    logger.info("=" * 80)

    if len(json_test_user_exclude) < len(json_test_user_full):
        logger.info(" exclude_unset=True уменьшил размер JSON для test_user")
        logger.info(f" Разница: {len(json_test_user_full) - len(json_test_user_exclude)} символов")

    if len(json_creation_exclude) < len(json_creation_full):
        logger.info(" exclude_unset=True уменьшил размер JSON для creation_user_data")
        logger.info(f" Разница: {len(json_creation_full) - len(json_creation_exclude)} символов")

    # Проверяем, какие поля исключены
    test_user_dict_exclude = user_from_test.model_dump(exclude_unset=True)
    test_user_dict_full = user_from_test.model_dump()

    excluded_fields = set(test_user_dict_full.keys()) - set(test_user_dict_exclude.keys())
    logger.info(f"\n Для test_user исключены поля: {excluded_fields}")

    creation_user_dict_exclude = user_from_creation.model_dump(exclude_unset=True)
    creation_user_dict_full = user_from_creation.model_dump()

    excluded_fields_creation = set(creation_user_dict_full.keys()) - set(creation_user_dict_exclude.keys())
    logger.info(f" Для creation_user_data исключены поля: {excluded_fields_creation}")


class TestUserValidation:
    """Тесты кастомных валидаторов Pydantic"""

    def test_valid_user(self):
        """Успешная валидация: все поля корректны"""
        user_data = {
            "email": "test@example.com",
            "fullName": "John Doe",
            "password": "SecurePass123!",
            "passwordRepeat": "SecurePass123!",
            "roles": [Roles.USER]
        }

        user = RegisteredUser(**user_data)

        assert user.email == "test@example.com"
        assert user.password == "SecurePass123!"
        logger.info(f" Успешная валидация: email={user.email}")

    def test_invalid_email_no_at_symbol(self):
        """ Ошибка: email без @"""
        user_data = {
            "email": "testexample.com",  # ← Нет @
            "fullName": "John Doe",
            "password": "SecurePass123!",
            "passwordRepeat": "SecurePass123!",
            "roles": [Roles.USER]
        }

        with pytest.raises(ValidationError) as exc_info:
            RegisteredUser(**user_data)

        # Проверяем, что ошибка именно в email
        errors = exc_info.value.errors()
        assert any(err['loc'] == ('email',) for err in errors)
        assert any('@"' in err['msg'] for err in errors)

        logger.info("Правильно отловлена ошибка: email без @")
        logger.error(f" Ошибка валидации: {errors[0]['msg']}")

    def test_invalid_password_too_short(self):
        """ Ошибка: пароль короче 8 символов"""
        user_data = {
            "email": "test@example.com",
            "fullName": "John Doe",
            "password": "short",  # ← Всего 5 символов
            "passwordRepeat": "short",
            "roles": [Roles.USER]
        }

        with pytest.raises(ValidationError) as exc_info:
            RegisteredUser(**user_data)

        errors = exc_info.value.errors()
        assert any(err['loc'] == ('password',) for err in errors)
        assert any('8 символов' in err['msg'] for err in errors)

        logger.info(" Правильно отловлена ошибка: короткий пароль")
        logger.error(f"  Ошибка валидации: {errors[0]['msg']}")

    def test_password_mismatch(self):
        """ Ошибка: passwordRepeat не совпадает с password"""
        user_data = {
            "email": "test@example.com",
            "fullName": "John Doe",
            "password": "SecurePass123!",
            "passwordRepeat": "DifferentPass456!",  # ← Не совпадает
            "roles": [Roles.USER]
        }

        with pytest.raises(ValidationError) as exc_info:
            RegisteredUser(**user_data)

        errors = exc_info.value.errors()
        assert any(err['loc'] == ('passwordRepeat',) for err in errors)
        assert any('совпадать' in err['msg'] for err in errors)

        logger.info(" Правильно отловлена ошибка: пароли не совпадают")
        logger.error(f"  Ошибка валидации: {errors[0]['msg']}")

    def test_multiple_validation_errors(self):
        """ Несколько ошибок одновременно"""
        user_data = {
            "email": "invalid-email",  # ← Нет @
            "fullName": "John Doe",
            "password": "123",  # ← Короткий
            "passwordRepeat": "456",  # ← Не совпадает
            "roles": [Roles.USER]
        }

        with pytest.raises(ValidationError) as exc_info:
            RegisteredUser(**user_data)

        errors = exc_info.value.errors()

        # Проверяем, что поймано несколько ошибок
        error_fields = [err['loc'][0] for err in errors]
        assert 'email' in error_fields
        assert 'password' in error_fields

        logger.info(" Правильно отловлены множественные ошибки:")
        for err in errors:
            logger.error(f"  - {err['loc'][0]}: {err['msg']}")

    def test_edge_cases(self):
        """Граничные случаи"""

        # Пароль ровно 8 символов (должен пройти)
        user_data = {
            "email": "test@example.com",
            "fullName": "John Doe",
            "password": "12345678",  # ← Ровно 8 символов
            "passwordRepeat": "12345678",
            "roles": [Roles.USER]
        }

        user = RegisteredUser(**user_data)
        assert user.password == "12345678"
        logger.info(" Пароль ровно 8 символов: валидация пройдена")

        # Пароль 7 символов (должен упасть)
        user_data["password"] = "1234567"
        user_data["passwordRepeat"] = "1234567"

        with pytest.raises(ValidationError):
            RegisteredUser(**user_data)

        logger.info(" Пароль 7 символов: валидация не пройдена")