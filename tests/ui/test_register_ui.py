from playwright.sync_api import Page
from tests.ui.pages.register_page import CinescopeRegisterPage
from random import randint, choice


def test_user_registration(page: Page):
    """Тест регистрации пользователя"""

    # Генерируем уникальный email
    unique_email = f"user_{randint(1000, 9999)}@test.ru"

    # Генерируем имя ТОЛЬКО из букв (без цифр!)
    # Можно использовать список имен или просто статическую строку с рандомом
    first_names = ["Александр", "Дмитрий", "Максим", "Сергей", "Андрей"]
    last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Попов"]

    # Выбираем случайные имя и фамилию
    full_name = f"{choice(first_names)} {choice(last_names)}"

    # Строгий пароль
    password = "Test@1234"

    register_page = CinescopeRegisterPage(page)
    register_page.open()

    register_page.register(
        full_name=full_name,
        email=unique_email,
        password=password,
        confirm_password=password
    )

    # Ждём редирект на логин
    register_page.wait_redirect_to_login_page()

    register_page.check_alert("Подтвердите свою почту")

    print(f"✅ Регистрация успешна! Пользователь: {full_name}")