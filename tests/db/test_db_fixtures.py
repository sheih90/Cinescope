# tests/db/test_db_fixtures.py
import pytest
import logging
from sqlalchemy import text  # ← Добавь этот импорт!
from db_requester.db_helpers import DBHelper
from db_models.user import UserDBModel
from db_models.movies import MovieDBModel
from utils.data_generator import DataGenerator

logger = logging.getLogger(__name__)


class TestDBFixtures:
    """Тесты для проверки фикстур БД"""

    def test_db_session_fixture(self, db_session):
        """Тест: фикстура db_session работает"""
        assert db_session is not None
        # ✅ Исправление: оборачиваем запрос в text()
        result = db_session.execute(text("SELECT 1;"))
        assert result is not None
        logger.info("✅ db_session fixture работает")

    def test_db_helper_fixture(self, db_helper):
        """Тест: фикстура db_helper работает"""
        assert db_helper is not None
        assert hasattr(db_helper, 'create_test_user')
        assert hasattr(db_helper, 'get_user_by_email')
        logger.info("✅ db_helper fixture работает")

    def test_created_test_user_fixture(self, created_test_user: UserDBModel):
        """Тест: фикстура created_test_user создаёт и удаляет пользователя"""
        assert created_test_user is not None
        assert created_test_user.id is not None
        assert created_test_user.email is not None

        logger.info(f"✅ Создан тестовый пользователь: {created_test_user.email}")

    def test_created_test_movie_fixture(self, created_test_movie: MovieDBModel):
        """Тест: фикстура created_test_movie создаёт и удаляет фильм"""
        assert created_test_movie is not None
        assert created_test_movie.id is not None
        assert created_test_movie.name is not None
        assert created_test_movie.location in ["MSK", "SPB"]

        logger.info(f"✅ Создан тестовый фильм: {created_test_movie.name}")

    def test_helper_methods(self, db_helper: DBHelper):
        """Тест: методы DBHelper работают"""
        # ✅ Исправление: используем generate_user_data_for_db() для БД!
        user = db_helper.create_test_user(DataGenerator.generate_user_data_for_db())

        # Проверяем получение по email
        found_user = db_helper.get_user_by_email(user.email)
        assert found_user is not None
        assert found_user.id == user.id

        # Проверяем exists
        assert db_helper.user_exists_by_email(user.email) is True

        # Проверяем получение по ID
        found_by_id = db_helper.get_user_by_id(user.id)
        assert found_by_id is not None

        # Cleanup
        db_helper.delete_user(user)

        # Проверяем, что удалён
        assert db_helper.get_user_by_id(user.id) is None

        logger.info("✅ Все методы DBHelper работают корректно")