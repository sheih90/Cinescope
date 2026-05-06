import random
import string
import datetime
from uuid import uuid4
from faker import Faker

faker = Faker('ru_RU')  # ← Добавил локаль для русских имён


class DataGenerator:
    """Генератор тестовых данных для API и БД"""

    # ========== БАЗОВЫЕ ГЕНЕРАТОРЫ ==========

    @staticmethod
    def generate_random_email(domain: str = "gmail.com") -> str:
        """Генерирует случайный email"""
        random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return f"kek{random_string}@{domain}"

    @staticmethod
    def generate_random_name() -> str:
        """Генерирует случайное имя"""
        return f"{faker.first_name()} {faker.last_name()}"

    @staticmethod
    def generate_random_password(length: int = None) -> str:
        """
        Генерация пароля, соответствующего требованиям:
        - Минимум 1 буква.
        - Минимум 1 цифра.
        - Допустимые символы.
        - Длина от 8 до 20 символов.
        """
        if length is None:
            length = random.randint(8, 20)

        # Гарантируем наличие хотя бы одной буквы и одной цифры
        letters = random.choice(string.ascii_letters)
        digits = random.choice(string.digits)

        # Дополняем пароль случайными символами
        special_chars = "?@#$%^&*|:"
        all_chars = string.ascii_letters + string.digits + special_chars
        remaining_length = max(0, length - 2)
        remaining_chars = ''.join(random.choices(all_chars, k=remaining_length))

        # Перемешиваем пароль
        password = list(letters + digits + remaining_chars)
        random.shuffle(password)

        return ''.join(password)

    # ========== ГЕНЕРАТОРЫ ДЛЯ API (старые методы) ==========

    @staticmethod
    def generate_user_data(email=None, full_name=None, password=None) -> dict:
        """
        Генерация данных для регистрации пользователя через API.

        Возвращает dict в формате, который ожидает эндпоинт POST /register.
        """
        pwd = password or DataGenerator.generate_random_password()
        return {
            "email": email or DataGenerator.generate_random_email(),
            "fullName": full_name or DataGenerator.generate_random_name(),
            "password": pwd,
            "passwordRepeat": pwd,  # Для API нужно повторить пароль
            "roles": ["USER"]  # API ожидает список
        }

    @staticmethod
    def generate_login_data(email=None, password=None) -> dict:
        """Генерация данных для логина через API"""
        return {
            "email": email or DataGenerator.generate_random_email(),
            "password": password or DataGenerator.generate_random_password()
        }

    # ========== ГЕНЕРАТОРЫ ДЛЯ БАЗЫ ДАННЫХ (новые методы) ==========

    @staticmethod
    def generate_user_data_for_db(
            email: str = None,
            full_name: str = None,
            password: str = None,
            verified: bool = False,
            banned: bool = False,
            roles: str = None
    ) -> dict:
        """
        Генерация данных для создания пользователя напрямую в БД.

        Возвращает dict, совместимый с моделью UserDBModel.

        :param email: Email пользователя
        :param full_name: Полное имя
        :param password: Пароль (хэшируется на уровне приложения)
        :param verified: Статус верификации
        :param banned: Статус блокировки
        :param roles: Роли в формате строки БД, например '{USER}'
        """
        pwd = password or DataGenerator.generate_random_password()
        now = datetime.datetime.now()

        return {
            'id': str(uuid4()),  # UUID как строка (тип в БД: text/uuid)
            'email': email or DataGenerator.generate_random_email(),
            'full_name': full_name or DataGenerator.generate_random_name(),  # snake_case!
            'password': pwd,  # В реальных тестах здесь должен быть хэш!
            'created_at': now,
            'updated_at': now,
            'verified': verified,
            'banned': banned,
            'roles': roles or '{USER}'  # Формат массива в PostgreSQL: {USER,ADMIN}
        }

    @staticmethod
    def generate_movie_data(
            name: str = None,
            genre_id: int = 1,
            location: str = None,
            published: bool = None
    ) -> dict:
        """
        Генерация данных для создания фильма напрямую в БД.

        Возвращает dict, совместимый с моделью MovieDBModel.

        :param name: Название фильма
        :param genre_id: ID жанра (должен существовать в БД)
        :param location: Локация (MSK или SPB — ENUM значения)
        :param published: Статус публикации
        """
        now = datetime.datetime.now()

        return {
            'name': name or faker.sentence(nb_words=4),
            'price': random.randint(100, 2000),
            'description': faker.paragraph(nb_sentences=3),
            'image_url': f"https://example.com/images/{uuid4()}.jpg",
            'location': location or random.choice(["MSK", "SPB"]),  # ENUM: только эти значения!
            'published': published if published is not None else random.choice([True, False]),
            'rating': round(random.uniform(0, 10), 1),
            'genre_id': genre_id,
            'created_at': now
        }

    # ========== УТИЛИТЫ ==========

    @staticmethod
    def get_random_location() -> str:
        """Возвращает случайное допустимое значение для location"""
        return random.choice(["MSK", "SPB"])

    @staticmethod
    def get_random_role_string(roles: list = None) -> str:
        """
        Конвертирует список ролей в формат строки PostgreSQL.

        Пример: ["USER", "ADMIN"] → "{USER,ADMIN}"
        """
        if roles is None:
            roles = ["USER"]
        return "{" + ",".join(roles) + "}"