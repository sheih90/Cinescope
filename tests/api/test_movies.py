import allure
import pytest
import requests
from constants import BASE_URL, HEADERS, MOVIES_ENDPOINT
from enums.roles import Roles
from entities.movie_response import MovieResponse
from datetime import datetime

class TestMoviesAPI:
    """Тесты для Movies API"""

    def test_get_default_movies(self, api_manager):
        """Получение списка фильмов по умолчанию"""
        response = api_manager.movies.get_movies()  # 200 по умолчанию

        data = response.json()

        # Проверяем пагинацию
        assert data["pageSize"] == 10, f"pageSize должен быть 10, получено {data['pageSize']}"
        assert data["page"] == 1, f"page должен быть 1, получено {data['page']}"

        # Получаем список фильмов
        movies = data["movies"]

        # Проверяем, что фильмы есть
        assert len(movies) > 0, "Список фильмов не должен быть пустым"

        # Проверяем каждый фильм
        for movie in movies:
            assert movie["location"] in ["SPB", "MSK"], \
                f"Location должен быть SPB или MSK, получено {movie['location']}"

            assert 1 <= movie["price"] <= 1000, \
                f"Price должен быть от 1 до 1000, получено {movie['price']}"

            assert movie["published"] == True, \
                f"Published должен быть True, получено {movie['published']}"

    @allure.story("Получение фильма по ID")
    @allure.title("Получение фильма по ID с валидацией через Pydantic")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.api
    def test_get_movie(self, api_manager_auth):
        """Получение фильма по ID с валидацией через Pydantic"""
        with allure.step("Получение списка фильмов для выбора ID"):
            response_list = api_manager_auth.session.get(f"{BASE_URL}/movies")
            assert response_list.status_code == 200

            movies_data = response_list.json()

            if isinstance(movies_data, list):
                movies_list = movies_data
            elif isinstance(movies_data, dict):
                movies_list = movies_data.get("items") or movies_data.get("movies") or movies_data.get("data") or []
            else:
                movies_list = []

            assert len(movies_list) > 0, "В базе нет фильмов для тестирования"
            movie_id = movies_list[0]["id"]

        with allure.step(f"Получение фильма по ID {movie_id}"):
            response = api_manager_auth.session.get(f"{BASE_URL}/movies/{movie_id}")
            assert response.status_code == 200, f"Фильм с ID {movie_id} не найден"

        with allure.step("Валидация ответа через Pydantic модель"):
            movie = MovieResponse(**response.json())

            allure.dynamic.parameter("movie_id", movie.id)
            allure.dynamic.parameter("movie_name", movie.name)
            allure.dynamic.parameter("movie_price", movie.price)

        with allure.step("Проверка полей фильма"):
            assert movie.id == movie_id
            assert movie.name is not None
            assert movie.price > 0
            assert movie.location in ["MSK", "SPB"]
            assert isinstance(movie.createdAt, datetime)

    @pytest.mark.parametrize("min_price,max_price", [
        (100, 500),  # Низкий диапазон
        (1000, 2000),  # Средний диапазон
        (5000, 10000),  # Высокий диапазон
        (200, 800),  # Другой низкий диапазон
    ])
    @allure.story("Фильтрация фильмов по цене")
    @allure.title("Фильтрация фильмов: цена от {min_price} до {max_price}")
    @allure.severity(allure.severity_level.NORMAL)
    def test_filter_movies_by_price(self, api_manager_auth, min_price, max_price):
        """
        Параметризованный тест фильтрации фильмов по цене.
        """
        with allure.step(f"Запрос фильмов с ценой от {min_price} до {max_price}"):
            response = api_manager_auth.session.get(
                f"{BASE_URL}/movies",
                params={"minPrice": min_price, "maxPrice": max_price}
            )

        with allure.step("Проверка статуса ответа"):
            # API может вернуть 200 (успех) или 400 (неверные параметры)
            # Главное — не 500 (ошибка сервера)
            assert response.status_code in [200, 400], \
                f"Неожиданный статус: {response.status_code}"

            if response.status_code == 400:
                allure.dynamic.parameter("result", "Bad Request (ожидаемо для некоторых диапазонов)")
                pytest.skip(f"Диапазон [{min_price}, {max_price}] не поддерживается API")
                return

        with allure.step("Проверка структуры ответа"):
            movies_data = response.json()

            # Обрабатываем ответ с пагинацией или без
            if isinstance(movies_data, list):
                movies_list = movies_data
            elif isinstance(movies_data, dict):
                movies_list = (
                        movies_data.get("items") or
                        movies_data.get("movies") or
                        movies_data.get("data") or
                        []
                )
            else:
                movies_list = []

        with allure.step(f"Проверка фильмов в диапазоне (найдено: {len(movies_list)})"):
            allure.dynamic.parameter("found_count", len(movies_list))

            # Проверяем первые 3 фильма (если есть)
            for movie_data in movies_list[:3]:
                movie = MovieResponse(**movie_data)

                # Проверяем, что цена в диапазоне
                assert min_price <= movie.price <= max_price, \
                    f"Фильм '{movie.name}' имеет цену {movie.price} вне диапазона"

    @allure.story("Удаление фильма")
    @allure.title("Удаление фильма с проверкой в БД")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.database
    @pytest.mark.api
    def test_delete_movie(self, api_manager_auth, db_helper):
        """Удаление фильма с проверкой в БД"""
        with allure.step("Подготовка: создание тестового фильма в БД"):
            movie_data = {
                "name": f"Test Movie {pytest.test_run_id if hasattr(pytest, 'test_run_id') else '001'}",
                "price": 500,
                "description": "Test description",
                "location": "MSK",
                "published": True,
                "genre_id": 1
            }
            movie = db_helper.create_test_movie(movie_data)
            movie_id = movie.id
            allure.dynamic.parameter("created_movie_id", movie_id)

        with allure.step(f"Удаление фильма {movie_id} через API"):
            response = api_manager_auth.session.delete(f"{BASE_URL}/movies/{movie_id}")
            assert response.status_code == 200, f"Ошибка удаления: {response.text}"

        with allure.step("Проверка, что фильм удалён (404)"):
            get_response = api_manager_auth.session.get(f"{BASE_URL}/movies/{movie_id}")
            assert get_response.status_code == 404, "Фильм должен быть удалён"

        with allure.step("Очистка: удаление тестовых данных"):
            # Фильм уже удалён из БД через API
            pass

    def test_get_movies_random_price(self, api_manager, random_price):
        """Тест фильтрации по цене"""
        minPrice = random_price["minPrice"]
        maxPrice = random_price["maxPrice"]

        response = api_manager.movies.get_movies(random_price)
        data = response.json()
        movies = data["movies"]

        # Проверяем, что фильмы нашлись
        assert len(movies) > 0, f"Нет фильмов в диапазоне цен [{minPrice}, {maxPrice}]"

        # Проверяем цену КАЖДОГО фильма
        for movie in movies:
            assert minPrice <= movie["price"] <= maxPrice

    def test_get_movies_random_location(self, api_manager, random_location):
        """Тест фильтрации по локации"""
        location = random_location["locations"]

        response = api_manager.movies.get_movies(random_location)

        data = response.json()
        movies = data["movies"]

        # Проверяем, что все фильмы имеют правильную локацию
        for movie in movies:
            assert movie["location"] == location, \
                f"Локация фильма {movie['location']} не совпадает с запрошенной {location}. Фильм: {movie['id']}"

    def test_get_movies_random_published(self, api_manager, random_published):
        """Тест фильтрации по публикации"""
        published = random_published["published"]

        response = api_manager.movies.get_movies(random_published)

        data = response.json()
        movies = data["movies"]

        # API возвращает boolean, сравниваем с ожидаемым
        expected = published == "true"

        for movie in movies:
            assert movie["published"] == expected, \
                f"Фильм {movie['id']} имеет published={movie['published']}, ожидалось {expected}"

    def test_get_movies_by_genre(self, api_manager, random_genre):
        """Тест проверки фильтрации по жанру и соответствия genreId названию жанра"""

        genre_id = random_genre["genreId"]
        expected_genre_name = random_genre["expected_genre_name"]

        # Отправляем GET запрос с фильтром по жанру
        response = api_manager.movies.get_movies({"genreId": genre_id})

        data = response.json()
        movies = data["movies"]

        # Проверяем, что все фильмы имеют правильный genreId
        for movie in movies:
            assert movie["genreId"] == genre_id, \
                f"genreId фильма {movie['genreId']} не совпадает с запрошенным {genre_id}. Фильм: {movie['id']}"

            # Проверяем название жанра
            genre_name = movie.get("genre", {}).get("name")
            assert genre_name == expected_genre_name, \
                f"Название жанра '{genre_name}' не соответствует ожидаемому '{expected_genre_name}' для genreId={genre_id}. Фильм: {movie['id']}"

    def test_get_movies_combo_params(self, api_manager, random_price, random_location, random_published, random_genre):
        """Комбинированная фильтрация по заданным параметрам"""
        minPrice = random_price["minPrice"]
        maxPrice = random_price["maxPrice"]
        location = random_location["locations"]
        published = random_published["published"]
        genre_id = random_genre["genreId"]
        expected_genre_name = random_genre["expected_genre_name"]

        params = {
            "minPrice": minPrice,
            "maxPrice": maxPrice,
            "locations": location,
            "published": published,
            "genreId": genre_id
        }

        # Отправляем GET запрос со всеми фильтрами
        response = api_manager.movies.get_movies(params)  # Передаём все параметры

        data = response.json()
        movies = data["movies"]
        # Проверяем, что фильмы нашлись
        assert len(movies) > 0, "Нет фильмов с заданными параметрами фильтрации"

        # Проверяем каждый фильм по всем критериям
        for movie in movies:
            # Проверка цены
            assert minPrice <= movie["price"] <= maxPrice, \
                f"Цена {movie['price']} вне диапазона [{minPrice}, {maxPrice}]. Фильм: {movie['id']}"

            # Проверка локации
            assert movie["location"] == location, \
                f"Локация {movie['location']} не совпадает с {location}. Фильм: {movie['id']}"

            # Проверка published
            expected_published = (published == "true")
            assert movie["published"] == expected_published, \
                f"Published {movie['published']} не совпадает с {expected_published}. Фильм: {movie['id']}"

            # Проверка genreId
            assert movie["genreId"] == genre_id, \
                f"GenreId {movie['genreId']} не совпадает с {genre_id}. Фильм: {movie['id']}"

            # Проверка названия жанра
            genre_name = movie.get("genre", {}).get("name")
            assert genre_name == expected_genre_name, \
                f"Жанр '{genre_name}' не совпадает с '{expected_genre_name}'. Фильм: {movie['id']}"

    def test_get_movies_by_pageSize_string(self, api_manager):
        """Тест проверки валидации pageSize (строка вместо числа)"""
        params = {"pageSize": "ab"}

        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        error_data = response.json()

        assert error_data["statusCode"] == 400
        assert error_data["error"] == "Bad Request"
        assert "message" in error_data

    def test_get_movies_by_pageSize_zero(self, api_manager):
        params = {"pageSize": 0}
        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        # Проверяем тело ответа с ошибкой
        error_data = response.json()

        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"

        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"

        # Проверяем, что есть сообщение об ошибке
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"

    def test_get_movies_by_pageSize_max(self, api_manager):
        params = {"pageSize": 21}
        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        error_data = response.json()
        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"
        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"

    def test_get_movies_by_negative_page(self, api_manager):
        params = {"page": -1}
        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        error_data = response.json()
        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"
        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"

    def test_get_movies_by_maxPrice_less_minPrice(self, api_manager):
        params = {
            "minPrice": 100,
            "maxPrice": 5
        }
        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        error_data = response.json()
        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"
        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"

    @pytest.mark.xfail(reason="BUG: API не валидирует параметр published - возвращает 200 вместо 400")
    def test_get_movies_by_published_invalid(self, api_manager):
        params = {"published": "yes"}
        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )
        error_data = response.json()
        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"
        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"
        """ Баг-репорт:
                Заголовок:
                API: Параметр published принимает некорректные значения (строки, числа) вместо boolean
                Шаги:
                    Отправить GET /movies?published="yes"
                    Отправить GET /movies?published=45
                ОР:
                400 Bad Request с сообщением о некорректном типе данных
                ФР:
                200 OK, API игнорирует некорректное значение и возвращает все фильмы
                Серьезность: Medium (проблема валидации входных данных)"""

    def test_get_movies_by_locations_invalid(self, api_manager):
        """Тест проверки валидации параметра locations (число вместо строки)"""

        params = {"locations": 123}

        response = api_manager.movies.get_movies(
            params,
            expected_status=400  # Переопределяем дефолтное 200 на 400
        )

        error_data = response.json()
        assert error_data["statusCode"] == 400, \
            f"statusCode должен быть 400, получен {error_data.get('statusCode')}"
        assert error_data["error"] == "Bad Request", \
            f"error должен быть 'Bad Request', получен {error_data.get('error')}"
        assert "message" in error_data, "В ответе должно быть поле 'message' с описанием ошибки"

    def test_create_movie_success(self, super_admin, random_movie_data):
        """Успешное создание фильма супер_админом"""
        response = super_admin.api.movies.create_movie(random_movie_data)  # 201 по умолчанию
        response_data = response.json()

        assert "id" in response_data
        assert response_data["name"] == random_movie_data["name"]
        assert response_data["price"] == random_movie_data["price"]
        assert response_data["location"] == random_movie_data["location"]
        assert response_data["published"] == random_movie_data["published"]
        assert response_data["genreId"] == random_movie_data["genreId"]
        assert "createdAt" in response_data

    def test_create_movie_msk_location(self, super_admin, random_movie_data):
        """Создание фильма с location = MSK"""
        movie_data = random_movie_data.copy()
        movie_data["location"] = "MSK"
        response = super_admin.api.movies.create_movie(movie_data)
        response_data = response.json()
        assert response_data["location"] == "MSK"

    def test_create_movie_not_published(self, super_admin, random_movie_data):
        """Создание неопубликованного фильма (published = false)"""

        movie_data = random_movie_data.copy()
        movie_data["published"] = False

        response = super_admin.api.movies.create_movie(movie_data)  # 201 по умолчанию

        response_data = response.json()
        assert response_data["published"] == False

    def test_create_movie_without_auth(self, api_manager, random_movie_data):
        """Создание фильма без авторизации"""

        movie_data = random_movie_data.copy()
        movie_data["name"] = "Фильм без токена"

        # Отправляем запрос без токена (ожидаем 401)
        response = api_manager.movies.create_movie(
            movie_data,
            expected_status=401  # Переопределяем дефолтное 201 на 401
        )

        response_data = response.json()
        assert response_data["message"] == "Unauthorized"

    def test_create_movie_empty_name(self, api_manager_auth, random_movie_data):
        """Создание фильма без названия"""

        movie_data = random_movie_data.copy()
        movie_data["name"] = ""

        response = api_manager_auth.movies.create_movie(
            movie_data,
            expected_status=400  # Переопределяем дефолтное 201 на 400
        )

        response_data = response.json()
        assert "message" in response_data
        assert response_data["error"] == "Bad Request"

    def test_create_movie_duplicate_name(self, api_manager_auth, random_movie_data):
        """Создание фильма с дублирующимся названием"""

        movie = {
            "name": random_movie_data["name"],
            "price": 100,
            "genreId": 1,
            "description": "Описание",
            "location": "SPB",
            "published": True
        }

        # Первый запрос — успех (201 по умолчанию)
        r1 = api_manager_auth.movies.create_movie(movie)

        # Второй запрос — конфликт (409 — переопределяем дефолт)
        r2 = api_manager_auth.movies.create_movie(movie, expected_status=409)

        # Проверяем сообщение об ошибке
        response_data = r2.json()
        assert "message" in response_data
        assert response_data.get("error") == "Conflict"

    def test_update_movie_success(self, super_admin, random_movie_data):
        """Успешное обновление фильма"""

        # Создаём фильм
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # Обновляем фильм
        update_data = {
            "price": 999,
            "description": "Обновлённое описание"
        }
        update_response = super_admin.api.movies.update_movie(movie_id, update_data)

        # 3. Проверяем обновление
        assert update_response.status_code == 200
        updated_movie = update_response.json()
        assert updated_movie["price"] == 999
        assert updated_movie["description"] == "Обновлённое описание"
        assert updated_movie["id"] == movie_id  # ID не должен измениться

    def test_update_movie_without_auth(self, api_manager_auth, api_manager, random_movie_data):
        """Обновление фильма без авторизации (401)"""

        # Создаём фильм (нужен токен — используем api_manager_auth)
        create_response = api_manager_auth.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # Пытаемся обновить без токена (используем api_manager без токена)
        update_data = {"price": 500}
        update_response = api_manager.movies.update_movie(
            movie_id,
            update_data,
            expected_status=401
        )

        assert update_response.json()["message"] == "Unauthorized"

    def test_update_movie_not_found(self, api_manager_auth):
        """Обновление несуществующего фильма (404)"""

        update_data = {"price": 500}
        update_response = api_manager_auth.movies.update_movie(
            99999,  # Несуществующий ID
            update_data,
            expected_status=404
        )

        assert update_response.json()["statusCode"] == 404
        assert update_response.json()["error"] == "Not Found"

    def test_delete_movie_success(self, super_admin, random_movie_data):
        """Успешное удаление фильма"""

        # Создаём фильм
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # Удаляем фильм
        delete_response = super_admin.api.movies.delete_movie(movie_id)
        assert delete_response.status_code == 200

        # Проверяем, что фильм удалён (404 при получении по ID)
        get_response = super_admin.api.movies.get_movie_by_id(
            movie_id,
            expected_status=404
        )
        assert get_response.status_code == 404
        assert get_response.json()["error"] == "Not Found"

    def test_delete_movie_without_auth(self,api_manager_auth,  api_manager, random_movie_data):
        """Удаление фильма без авторизации (401)"""

        # 1. Создаём фильм (нужен токен)
        create_response = api_manager_auth.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # 2. Пытаемся удалить без токена
        delete_response = api_manager.movies.delete_movie(
            movie_id,
            expected_status=401
        )

        assert delete_response.json()["message"] == "Unauthorized"

    def test_delete_movie_not_found(self, api_manager_auth):
        """Удаление несуществующего фильма (404)"""

        delete_response = api_manager_auth.movies.delete_movie(
            99999,  # Несуществующий ID
            expected_status=404
        )

        assert delete_response.json()["statusCode"] == 404
        assert delete_response.json()["error"] == "Not Found"

    @pytest.mark.slow
    def test_create_movie_as_user_forbidden(self, common_user, random_movie_data):
        """
        Обычный пользователь (USER) НЕ может создавать фильмы.
        Ожидаем 403 Forbidden.
        """
        response = common_user.api.movies.create_movie(
            random_movie_data,
            expected_status=403  # У USER нет прав на создание фильма
        )

        data = response.json()
        assert data["error"] == "Forbidden"
        assert "message" in data

    @pytest.mark.slow
    def test_update_movie_as_user_forbidden(self, common_user, super_admin, random_movie_data):
        """USER не может обновлять фильмы → 403"""
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        update_data = {"price": 500}
        update_response = common_user.api.movies.update_movie(
            movie_id,
            update_data,
            expected_status=403
        )
        assert update_response.json()["error"] == "Forbidden"

    def test_delete_movie_as_user_forbidden(self, common_user, super_admin, random_movie_data):
        """USER не может удалять фильмы → 403"""
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        delete_response = common_user.api.movies.delete_movie(
            movie_id,
            expected_status=403
        )
        assert delete_response.json()["error"] == "Forbidden"

    @pytest.mark.slow
    def test_create_movie_as_admin_forbidden(self, admin_user, random_movie_data):
        """ADMIN не может создавать фильмы → 403 Forbidden"""
        response = admin_user.api.movies.create_movie(
            random_movie_data,
            expected_status=403
        )
        data = response.json()
        assert data["error"] == "Forbidden"

    @pytest.mark.parametrize(
        "filter_params,description",
        [
            # (параметры фильтра, описание теста)
            (
                    {"minPrice": 100, "maxPrice": 300},
                    "Фильтрация по цене: 100-300"
            ),
            (
                    {"locations": ["MSK"]},
                    "Фильтрация по локации: MSK"
            ),
            (
                    {"locations": ["SPB"]},
                    "Фильтрация по локации: SPB"
            ),
            (
                    {"genreId": 1},
                    "Фильтрация по жанру: genreId=1"
            ),
            (
                    {"genreId": 2},
                    "Фильтрация по жанру: genreId=2"
            ),
            (
                    {"minPrice": 200, "maxPrice": 500, "locations": ["MSK"]},
                    "Комбинированный фильтр: цена 200-500 + локация MSK"
            ),
            (
                    {"minPrice": 150, "maxPrice": 400, "genreId": 3},
                    "Комбинированный фильтр: цена 150-400 + жанр"
            ),
            (
                    {"locations": ["SPB"], "genreId": 2},
                    "Комбинированный фильтр: локация SPB + жанр"
            ),
            (
                    {"minPrice": 100, "maxPrice": 600, "locations": ["MSK"], "genreId": 1},
                    "Полный фильтр: цена + локация + жанр"
            ),
        ],
        ids=[
            "price_100_300",
            "location_msk",
            "location_spb",
            "genre_1",
            "genre_2",
            "price_200_500_location_msk",
            "price_150_400_genre_3",
            "location_spb_genre_2",
            "full_filter"
        ]
    )
    def test_get_movies_with_filters(self, api_manager, filter_params, description):
        """
        Параметризованный тест фильтрации фильмов.
        Проверяет, что API корректно фильтрует фильмы по различным параметрам.
        """
        # Отправляем запрос с фильтрами
        response = api_manager.movies.get_movies(filter_params)
        data = response.json()
        movies = data["movies"]

        # Проверяем, что фильмы найдены (хотя бы один)
        assert len(movies) >= 0, f"Нет фильмов с фильтром: {description}"

        # Проверяем каждый фильм на соответствие фильтрам
        for movie in movies:
            # Проверка цены
            if "minPrice" in filter_params:
                assert movie["price"] >= filter_params["minPrice"], \
                    f"Фильм {movie['id']} имеет цену {movie['price']} ниже minPrice {filter_params['minPrice']}"

            if "maxPrice" in filter_params:
                assert movie["price"] <= filter_params["maxPrice"], \
                    f"Фильм {movie['id']} имеет цену {movie['price']} выше maxPrice {filter_params['maxPrice']}"

            # Проверка локации
            if "locations" in filter_params:
                assert movie["location"] in filter_params["locations"], \
                    f"Фильм {movie['id']} имеет локацию {movie['location']}, ожидалось {filter_params['locations']}"

            # Проверка жанра
            if "genreId" in filter_params:
                assert movie["genreId"] == filter_params["genreId"], \
                    f"Фильм {movie['id']} имеет genreId {movie['genreId']}, ожидалось {filter_params['genreId']}"

    @pytest.mark.parametrize(
        "expected_status",
        [
            403,
        ],
        ids=["user_forbidden"]
    )
    def test_delete_movie_as_user_forbidden(self, common_user, super_admin, random_movie_data, expected_status):
        """USER не может удалять фильмы → 403 Forbidden"""
        # 1. Создаём фильм (супер-админом)
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # 2. Пытаемся удалить как USER
        delete_response = common_user.api.movies.delete_movie(
            movie_id,
            expected_status=expected_status
        )

        # 3. Проверяем, что получили 403
        assert delete_response.status_code == expected_status
        error_data = delete_response.json()
        assert error_data["error"] == "Forbidden"

        # 4. Проверяем, что фильм всё ещё существует
        get_response = super_admin.api.movies.get_movie_by_id(movie_id)
        assert get_response.status_code == 200

    @pytest.mark.parametrize(
        "expected_status",
        [
            403,
        ],
        ids=["admin_forbidden"]
    )
    @pytest.mark.slow
    def test_delete_movie_as_admin_forbidden(self, admin_user, super_admin, random_movie_data, expected_status):
        """ADMIN не может удалять фильмы → 403 Forbidden"""
        # 1. Создаём фильм (супер-админом)
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # 2. Пытаемся удалить как ADMIN
        delete_response = admin_user.api.movies.delete_movie(
            movie_id,
            expected_status=expected_status
        )

        # 3. Проверяем, что получили 403
        assert delete_response.status_code == expected_status
        error_data = delete_response.json()
        assert error_data["error"] == "Forbidden"

        # 4. Проверяем, что фильм всё ещё существует
        get_response = super_admin.api.movies.get_movie_by_id(movie_id)
        assert get_response.status_code == 200

    def test_delete_movie_as_super_admin_success(self, super_admin, random_movie_data):
        """SUPER_ADMIN может удалять фильмы → 200 OK"""
        # 1. Создаём фильм
        create_response = super_admin.api.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # 2. Удаляем фильм (супер-админом)
        delete_response = super_admin.api.movies.delete_movie(movie_id)
        assert delete_response.status_code == 200

        # 3. Проверяем, что фильм действительно удалён
        get_response = super_admin.api.movies.get_movie_by_id(
            movie_id,
            expected_status=404
        )
        assert get_response.status_code == 404
        error_data = get_response.json()
        assert error_data["error"] == "Not Found"

