import pytest
import requests
import random
from constants import BASE_URL, HEADERS, BASE_AUTH_URL,ADMIN_CREDENTIALS, LOGIN_ENDPOINT, REGISTER_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator
from faker import Faker
fake = Faker()
from clients.api_manager import ApiManager
from entities.user import User
from resources.user_creds import SuperAdminCreds
from enums.roles import Roles
import uuid
from entities.api_models import UserCreate, MovieCreate
from models.base_models import TestUser


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


@pytest.fixture(scope="session")
def valid_genres():
    """Получаем список валидных жанров из API (первые 10)"""
    response = requests.get(f"{BASE_URL}/genres")
    genres = response.json()
    # Берем первые 10 жанров
    return [genre["id"] for genre in genres[:10]]


@pytest.fixture
def random_movie_data():
    """Фикстура: данные фильма (словарь)"""
    import random

    return {
        "name": f"Тестовый фильм {random.randint(1000, 9999)}",
        "imageUrl": "https://example.com/image.png",
        "price": random.randint(100, 500),
        "description": "Описание тестового фильма",
        "location": random.choice(["MSK", "SPB"]),
        "published": True,
        "genreId": random.choice([1, 2, 3])
    }

@pytest.fixture
def random_movie_model(random_movie_data):
    """Фикстура: данные фильма как Pydantic модель"""
    return MovieCreate(**random_movie_data)

@pytest.fixture
def random_user():
    """Фикстура: случайный пользователь для регистрации"""
    user_data = DataGenerator.generate_user_data()
    # passwordRepeat должен совпадать с password
    user_data["passwordRepeat"] = user_data["password"]
    return user_data

@pytest.fixture
def random_user_data():
    """Фикстура: данные пользователя для создания супер-админом"""
    user_data = DataGenerator.generate_user_data()
    user_data["passwordRepeat"] = user_data["password"]
    user_data["verified"] = False
    user_data["banned"] = False
    return user_data

@pytest.fixture
def admin_credentials():
    """Фикстура: креды админа"""
    return {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

@pytest.fixture
def user_roles():
    """Фикстура возвращает доступные роли пользователей"""
    return {
        "USER": ["USER"],
        "ADMIN": ["USER", "ADMIN"],
        "SUPER_ADMIN": ["USER", "ADMIN", "SUPER_ADMIN"]
    }

@pytest.fixture(scope="function")
def test_user() -> TestUser:
    """Фикстура: данные пользователя (словарь)"""
    random_password = DataGenerator.generate_random_password()

    return TestUser(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]  # ✅ Передаём Enum, а не строку!
    )

@pytest.fixture
def creation_user_data(test_user: TestUser) -> dict:
    """Конвертирует TestUser в dict для отправки в API"""
    return test_user.to_json_for_api()

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
    registered_user = test_user.model_dump()
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

@pytest.fixture
def user_session():
    """Фикстура создания сессии юзера"""
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()


@pytest.fixture
def super_admin(user_session):
    """Фикстура супер-админа"""
    new_session = user_session()

    # Создаём объект User с кредами супер-админа
    super_admin = User(
        email=SuperAdminCreds.USERNAME,
        password=SuperAdminCreds.PASSWORD,
        roles=[Roles.SUPER_ADMIN.value],
        api=new_session
    )

    # Аутентифицируем супер-админа
    login_response = super_admin.api.auth.login_user(super_admin.creds)

    # ✅ ДОБАВЛЯЕМ ТОКЕН В ЗАГОЛОВКИ СЕССИИ!
    token = login_response.json()["accessToken"]
    new_session.auth.session.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return super_admin


@pytest.fixture(scope="function")
def creation_user_data(test_user):
    """
    Фикстура для создания пользователя через POST /user (супер-админом).
    Отличается от test_user наличием полей verified и banned.
    """
    updated_data = test_user.model_dump()
    updated_data.update({
        "verified": True,
        "banned": False,
        "roles": [Roles.USER.value]
    })
    return updated_data


@pytest.fixture
def common_user(user_session, super_admin, creation_user_data):
    """
    Фикстура обычного пользователя с ролью USER.
    Создаётся супер-админом, затем аутентифицируется.
    """
    # 1. Создаём новую сессию для этого пользователя
    new_session = user_session()

    # 2. Создаём объект User с данными из creation_user_data
    common_user = User(
        email=creation_user_data['email'],
        password=creation_user_data['password'],
        roles=[Roles.USER.value],  # Роль обычного пользователя
        api=new_session
    )

    # 3. Создаём пользователя через супер-админа
    super_admin.api.user.create_user(creation_user_data)

    # 4. Аутентифицируем созданного пользователя
    login_response = common_user.api.auth.login_user(common_user.creds)

    # 5. Добавляем токен в заголовки сессии
    token = login_response.json()["accessToken"]
    new_session.auth.session.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return common_user

@pytest.fixture
def admin_user(user_session, super_admin, creation_user_data):
    """
    Фикстура пользователя с ролью ADMIN.
    Создаётся супер-админом, затем аутентифицируется.
    """
    # 1. Создаём новую сессию для этого пользователя
    new_session = user_session()

    # 2. Создаём объект User с данными из creation_user_data (изначально роль USER)
    create_response = super_admin.api.user.create_user(creation_user_data)
    created_user_id = create_response.json()["id"]

    # 3. Обновляем пользователя: добавляем роль ADMIN
    update_data = {
        "verified": True,
        "banned": False,
        "roles": [Roles.USER.value, Roles.ADMIN.value]  # Добавляем ADMIN
    }
    super_admin.api.user.update_user(created_user_id, update_data)

    # 4. Создаём объект User с обновлёнными ролями
    admin_user = User(
        email=creation_user_data['email'],
        password=creation_user_data['password'],
        roles=[Roles.USER.value, Roles.ADMIN.value],  # Две роли
        api=new_session
    )

    # 5. Аутентифицируем (теперь у пользователя две роли)
    login_response = admin_user.api.auth.login_user(admin_user.creds)

    # 6. Добавляем токен в заголовки
    token = login_response.json()["accessToken"]
    new_session.auth.session.headers.update({
        "Authorization": f"Bearer {token}"
    })

    return admin_user

@pytest.fixture
def registration_user_data():
    random_password = DataGenerator.generate_random_password()

    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": random_password,
        "passwordRepeat": random_password,
        "roles": [Roles.USER.value]
    }