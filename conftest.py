import pytest
import requests
import random
from constants import BASE_URL, HEADERS, BASE_AUTH_URL,ADMIN_CREDENTIALS, LOGIN_ENDPOINT, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from faker import Faker
fake = Faker()
from clients.api_manager import ApiManager


@pytest.fixture(scope="session")
def api_session():
    """Фикстура создаёт сессию, которая используется на весь запуск тестов"""

    # Создаём сессию
    session = requests.Session()
    session.headers.update(HEADERS)

    # Логинимся через сессию
    response = session.post(
        f"{BASE_AUTH_URL}{LOGIN_ENDPOINT}",
        json=ADMIN_CREDENTIALS,
        headers=HEADERS
    )

    assert response.status_code == 200, f"Ошибка авторизации: {response.text}"

    # Получаем accessToken
    token = response.json().get("accessToken")
    assert token is not None, "В ответе не оказалось accessToken"

    # Добавляем токен в заголовки сессии
    session.headers.update({"Authorization": f"Bearer {token}"})  # ← Bearer токен!

    return session

@pytest.fixture(scope="session")
def api_manager_auth(api_session):
    """
    Фикстура для ApiManager с авторизованной сессией.
    Для тестов, где нужен токен (создание фильмов, управление пользователями).
    """
    return ApiManager(api_session)

@pytest.fixture
def random_pagination_params():
    """
    Фикстура генерирует случайные параметры пагинации.
    Вызывается перед каждым тестом.
    """
    page = random.randint(1, 100)
    page_size = random.randint(1, 20)

    return {
        "page": page,
        "pageSize": page_size
    }

@pytest.fixture
def random_price():
    """
    Фикстура генерирует случайные minPrice (от 1 до 10) и maxPrice(от 10 до 1000).
    """
    minPrice = random.randint(1, 10)
    maxPrice = random.randint(11, 1000)

    return {
        "minPrice": minPrice,
        "maxPrice": maxPrice
    }

@pytest.fixture
def random_location():
    """
    Фикстура генерирует случайную локацию: "MSK" или "SPB".
    """
    return {"locations": random.choice(["MSK", "SPB"])}

@pytest.fixture
def random_published():
    """
    Фикстура генерирует случайный статус публикации.
    """
    # Возвращаем строку в нижнем регистре, как ожидает API
    return {"published": random.choice(["true", "false"])}


@pytest.fixture
def random_genre():
    """
    Фикстура возвращает случайный genreId и ожидаемое название жанра.
    """
    genres_map = {
        1: "Драма",
        2: "Комедия",
        3: "Фантастика",
        4: "Криминал",
        5: "Триллер",
        6: "Аниме",
        7: "Мюзикл",
        8: "Фэнтези",
        9: "Анимация",
        10: "Военный"
    }
    genre_id = random.choice(list(genres_map.keys()))
    return {
        "genreId": genre_id,
        "expected_genre_name": genres_map[genre_id]
    }


@pytest.fixture
def random_movie_data():
    """Фикстура возвращает словарь с данными для тестового фильма"""

    return {
        "name": f"Тестовый фильм {random.randint(1000, 9999)}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(50, 500),
        "description": "Описание тестового фильма",
        "location": random.choice(["SPB", "MSK"]),
        "published": random.choice([True, False]),
        "genreId": random.randint(1, 10)
    }


@pytest.fixture
def random_user():
    """Фикстура возвращает словарь со случайными данными пользователя"""
    import random
    import string

    random_number = random.randint(1000, 9999)
    password = f"Test{random_number}@"

    first_names = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Henry",
                   "Александр", "Мария", "Дмитрий", "Анна", "Сергей", "Елена"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                  "Иванов", "Петрова", "Сидоров", "Козлова", "Новиков", "Волкова"]

    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"

    return {
        "email": fake.email(),
        "fullName": full_name,
        "password": password,
        "passwordRepeat": password
    }


@pytest.fixture
def random_user_data():
    """Фикстура генерирует данные для создания пользователя админом (POST /user)"""
    random_number = random.randint(1000, 9999)
    password = f"Test{random_number}@"

    return {
        "fullName": fake.name(),
        "email": fake.email(),
        "password": password,
        "verified": random.choice([True, False]),
        "banned": random.choice([True, False])
    }

@pytest.fixture
def user_roles():
    """Фикстура возвращает доступные роли пользователей"""
    return {
        "USER": ["USER"],
        "ADMIN": ["USER", "ADMIN"],
        "SUPER_ADMIN": ["USER", "ADMIN", "SUPER_ADMIN"]
    }

@pytest.fixture(scope="session")
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        "email": random_email,
        "fullName": random_name,
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": ["USER"]
    }

@pytest.fixture(scope="session")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    response = requester.send_request(
        method="POST",
        endpoint=REGISTER_ENDPOINT,
        data=test_user,
        expected_status=201
    )
    response_data = response.json()
    registered_user = test_user.copy()
    registered_user["id"] = response_data["id"]
    return registered_user

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_AUTH_URL)

@pytest.fixture(scope="session")
def api_requester(api_session):
    """Фикстура создаёт кастомный реквестер с авторизованной сессией"""
    return CustomRequester(session=api_session, base_url=BASE_AUTH_URL)

@pytest.fixture(scope="session")
def anon_requester():
    """Фикстура создаёт реквестер БЕЗ авторизации (для тестов на 401/403)"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return CustomRequester(session=session, base_url=BASE_AUTH_URL)

@pytest.fixture(scope="session")
def movies_requester(api_session):
    """Фикстура для movies API (фильмы)"""
    return CustomRequester(session=api_session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def anon_movies_requester():
    """Фикстура для movies API БЕЗ авторизации (тесты на 401)"""
    session = requests.Session()
    session.headers.update(HEADERS)
    return CustomRequester(session=session, base_url=BASE_URL)

@pytest.fixture(scope="session")
def session():
    """
    Фикстура для создания HTTP-сессии.
    Используется всеми API-классами через ApiManager.
    """
    http_session = requests.Session()
    # Добавляем базовые заголовки (если нужно)
    http_session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json"
    })
    yield http_session
    http_session.close()  # Закрываем сессию после всех тестов


@pytest.fixture(scope="session")
def api_manager(session):
    """
    Фикстура для создания экземпляра ApiManager.
    Предоставляет тестам единый интерфейс ко всем API.
    """
    return ApiManager(session)

@pytest.fixture(scope="session")
def api_manager_auth(api_session):
    """ApiManager с авторизацией (для создания пользователей, фильмов)"""
    return ApiManager(api_session)