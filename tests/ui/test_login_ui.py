# tests/ui/test_login_ui.py
from playwright.sync_api import Page
from tests.ui.pages.register_page import CinescopeRegisterPage
from tests.ui.pages.login_page import CinescopeLoginPage
from random import randint


def test_register_and_login(page: Page):
    """Полный тест: регистрация + вход"""

    # Генерируем уникальные данные
    unique_email = f"damir_test_{randint(1000, 9999)}@test.ru"
    password = "StrongPassword123"
    full_name = "Дамир Тестовый"

    print(f"📧 Email: {unique_email}")
    print(f"🔑 Пароль: {password}")

    # ========== ШАГ 1: РЕГИСТРАЦИЯ ==========
    register_page = CinescopeRegisterPage(page)
    register_page.open()

    register_page.register(
        full_name=full_name,
        email=unique_email,
        password=password,
        confirm_password=password
    )

    # Ждём редирект на страницу логина
    register_page.wait_redirect_to_login_page()

    print("✅ Регистрация успешна!")

    # ========== ШАГ 2: ЛОГИН ==========
    # Теперь мы уже на странице логина (после редиректа)
    login_page = CinescopeLoginPage(page)

    login_page.login(
        email=unique_email,
        password=password
    )

    # Проверяем редирект на главную
    login_page.wait_redirect_to_home_page()

    login_page.check_alert("Подтвердите свою почту")

    print("✅ Вход выполнен успешно!")