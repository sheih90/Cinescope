import allure
from .base_page import BasePage


class CinescopeLoginPage(BasePage):
    """Страница входа"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        # Локаторы
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']:has-text('Войти')"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"


    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        self.enter_text(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        self.enter_text(self.password_input, password)

    @allure.step("Нажать 'Войти'")
    def click_login_button(self):
        self.click(self.login_button)

    @allure.step("Логин: {email}")
    def login(self, email: str, password: str):
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    @allure.step("Ожидать главную страницу")
    def wait_redirect_to_home_page(self):
        # Используем универсальный метод из BasePage
        self.wait_redirect_to("https://dev-cinescope.coconutqa.ru/")

    @allure.step("Проверить уведомление о входе")
    def check_alert(self, text: str = "Вы вошли в аккаунт"):
        # Используем метод из BasePage с кастомным скриншотом
        super().check_alert(text, "login_success")