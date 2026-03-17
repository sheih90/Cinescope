import pytest
import requests
from constants import BASE_URL, HEADERS, MOVIES_ENDPOINT


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

    def test_get_movies_random_pagination(self, api_manager, random_pagination_params):
        """
        Тест пагинации со случайными параметрами.
        Каждый запуск использует новые random page и pageSize.
        """
        page = random_pagination_params["page"]
        page_size = random_pagination_params["pageSize"]

        response = api_manager.movies.get_movies(
            random_pagination_params  # Передаём параметры пагинации
        )
        # Получаем данные
        data = response.json()

        # Проверяем метаданные пагинации
        assert data["pageSize"] == page_size, \
            f"pageSize в ответе ({data['pageSize']}) не совпадает с запрошенным ({page_size})"
        assert data["page"] == page, \
            f"page в ответе ({data['page']}) не совпадает с запрошенным ({page})"

        # Получаем список фильмов
        movies = data["movies"]

        # Проверяем количество фильмов (не больше pageSize)
        assert len(movies) <= page_size, \
            f"Количество фильмов {len(movies)} превышает pageSize {page_size}"

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
        """📋 Баг-репорт:
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

    def test_create_movie_success(self, api_manager_auth, random_movie_data):
        """Успешное создание фильма"""

        response = api_manager_auth.movies.create_movie(random_movie_data)  # 201 по умолчанию
        response_data = response.json()

        assert "id" in response_data
        assert response_data["name"] == random_movie_data["name"]
        assert response_data["price"] == random_movie_data["price"]
        assert response_data["location"] == random_movie_data["location"]
        assert response_data["published"] == random_movie_data["published"]
        assert response_data["genreId"] == random_movie_data["genreId"]
        assert "createdAt" in response_data

    def test_create_movie_msk_location(self, api_manager_auth, random_movie_data):
        """Создание фильма с location = MSK"""
        movie_data = random_movie_data.copy()
        movie_data["location"] = "MSK"
        response = api_manager_auth.movies.create_movie(movie_data)
        response_data = response.json()
        assert response_data["location"] == "MSK"

    def test_create_movie_not_published(self, api_manager_auth, random_movie_data):
        """Создание неопубликованного фильма (published = false)"""

        movie_data = random_movie_data.copy()
        movie_data["published"] = False

        response = api_manager_auth.movies.create_movie(movie_data)  # 201 по умолчанию

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

    def test_update_movie_success(self, api_manager_auth, random_movie_data):
        """Успешное обновление фильма"""

        # Создаём фильм
        create_response = api_manager_auth.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # Обновляем фильм
        update_data = {
            "price": 999,
            "description": "Обновлённое описание"
        }
        update_response = api_manager_auth.movies.update_movie(movie_id, update_data)

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

    def test_delete_movie_success(self, api_manager_auth, random_movie_data):
        """Успешное удаление фильма"""

        # Создаём фильм
        create_response = api_manager_auth.movies.create_movie(random_movie_data)
        movie_id = create_response.json()["id"]

        # Удаляем фильм
        delete_response = api_manager_auth.movies.delete_movie(movie_id)
        assert delete_response.status_code == 200

        # Проверяем, что фильм удалён (404 при получении по ID)
        get_response = api_manager_auth.movies.get_movie_by_id(
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