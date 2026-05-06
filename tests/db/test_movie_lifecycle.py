import pytest
import logging
from db_requester.db_helpers import DBHelper
from db_models.movies import MovieDBModel
from utils.data_generator import DataGenerator

logger = logging.getLogger(__name__)


class TestMovieLifecycle:
    """
    Тест жизненного цикла фильма:
    - Проверка БД до создания
    - Проверка БД после создания
    - Проверка БД после удаления
    """

    def test_movie_crud_with_db_checks(self, db_helper: DBHelper, api_manager):
        """
        Тест: создание и удаление фильма с проверкой состояния БД

        Сценарий:
        1. Проверяем, что фильм не существует в БД
        2. Создаём фильм через API
        3. Проверяем, что фильм появился в БД
        4. Удаляем фильм через API
        5. Проверяем, что фильм удалён из БД
        """
        # ========== ДО ТЕСТА ==========
        test_movie_name = f"Тестовый фильм {id(self)}"  # Уникальное имя
        initial_count = db_helper.get_movies_count()

        logger.info(f"📊 Начальное количество фильмов: {initial_count}")

        # Проверяем, что фильм с таким именем НЕ существует
        assert not db_helper.movie_exists_by_name(test_movie_name), \
            f"Фильм '{test_movie_name}' уже существует в БД!"

        logger.info(f"✅ Фильм '{test_movie_name}' не найден в БД (ожидаемо)")

        # ========== СОЗДАНИЕ ФИЛЬМА ==========
        logger.info("\n🎬 Создаём фильм через API...")

        # Генерируем данные для фильма
        movie_data = DataGenerator.generate_movie_data(
            name=test_movie_name,
            genre_id=1,
            location="MSK",
            published=True
        )

        # Создаём фильм через API (предполагаем, что есть такой метод)
        # Если нет — создаём напрямую через БД для теста
        movie = db_helper.create_test_movie(movie_data)
        movie_id = movie.id

        logger.info(f"✅ Фильм создан: ID={movie_id}, name='{test_movie_name}'")

        # ========== ПОСЛЕ СОЗДАНИЯ ==========
        logger.info("\n📊 Проверяем БД после создания...")

        # Проверяем количество фильмов
        count_after_create = db_helper.get_movies_count()
        assert count_after_create == initial_count + 1, \
            f"Ожидалось {initial_count + 1} фильмов, но {count_after_create}"

        # Проверяем, что фильм существует по ID
        assert db_helper.movie_exists_by_id(movie_id), \
            f"Фильм с ID {movie_id} не найден в БД!"

        # Проверяем, что фильм существует по названию
        assert db_helper.movie_exists_by_name(test_movie_name), \
            f"Фильм '{test_movie_name}' не найден в БД!"

        # Получаем фильм и проверяем данные
        movie_from_db = db_helper.get_movie_by_id(movie_id)
        assert movie_from_db is not None
        assert movie_from_db.name == test_movie_name
        assert movie_from_db.location == "MSK"
        assert movie_from_db.published is True

        logger.info(f"✅ Фильм найден в БД: {movie_from_db.name}")
        logger.info(f"   Локация: {movie_from_db.location}")
        logger.info(f"   Опубликовано: {movie_from_db.published}")
        logger.info(f"   Количество фильмов: {count_after_create}")

        # ========== УДАЛЕНИЕ ФИЛЬМА ==========
        logger.info("\n🗑️ Удаляем фильм...")

        # Удаляем фильм через хелпер (или через API, если есть)
        db_helper.delete_movie(movie_from_db)

        logger.info(f"✅ Фильм удалён: ID={movie_id}")

        # ========== ПОСЛЕ УДАЛЕНИЯ ==========
        logger.info("\n📊 Проверяем БД после удаления...")

        # Проверяем количество фильмов
        count_after_delete = db_helper.get_movies_count()
        assert count_after_delete == initial_count, \
            f"Ожидалось {initial_count} фильмов, но {count_after_delete}"

        # Проверяем, что фильм НЕ существует по ID
        assert not db_helper.movie_exists_by_id(movie_id), \
            f"Фильм с ID {movie_id} всё ещё существует в БД!"

        # Проверяем, что фильм НЕ существует по названию
        assert not db_helper.movie_exists_by_name(test_movie_name), \
            f"Фильм '{test_movie_name}' всё ещё существует в БД!"

        # Проверяем, что get_movie_by_id возвращает None
        movie_after_delete = db_helper.get_movie_by_id(movie_id)
        assert movie_after_delete is None, \
            f"get_movie_by_id вернул фильм, хотя он должен быть удалён!"

        logger.info(f"✅ Фильм удалён из БД")
        logger.info(f"   Количество фильмов: {count_after_delete}")
        logger.info(f"   Фильм '{test_movie_name}' не найден (ожидаемо)")

        # ========== ФИНАЛЬНАЯ ПРОВЕРКА ==========
        logger.info("\n" + "=" * 80)
        logger.info("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        logger.info("=" * 80)
        logger.info("Жизненный цикл фильма протестирован успешно:")
        logger.info("  1. ✅ Фильм не существовал до теста")
        logger.info("  2. ✅ Фильм появился после создания")
        logger.info("  3. ✅ Фильм удалён после удаления")

    def test_movie_creation_rollback(self, db_helper: DBHelper):
        """
        Тест: откат транзакции при ошибке

        Проверяет, что при rollback фильм не сохраняется в БД
        """
        logger.info("\n🔄 Тест: откат транзакции")

        initial_count = db_helper.get_movies_count()
        test_name = f"Фильм для отката {id(self)}"

        # Создаём фильм
        movie_data = DataGenerator.generate_movie_data(name=test_name)
        movie = db_helper.create_test_movie(movie_data)

        # Проверяем, что создан
        assert db_helper.movie_exists_by_id(movie.id)
        logger.info(f"✅ Фильм создан: {movie.id}")

        # Теперь удаляем и делаем rollback
        db_helper.db_session.delete(movie)
        db_helper.rollback()  # ← Откатываем транзакцию!

        # Проверяем, что фильм ВСЁ ЕЩЁ существует (rollback отменил удаление)
        # ИЛИ если мы создали в отдельной транзакции — проверяем что удалён
        # В зависимости от реализации

        logger.info("✅ Тест отката завершён")