import allure
from .base_page import BasePage


class CinescopeRegisterPage(BasePage):
    """Страница регистрации"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # Локаторы
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"
        self.register_button = "button[type='submit']:has-text('Зарегистрироваться')"


    @allure.step("Ввести ФИО: {full_name}")
    def enter_full_name(self, full_name: str):
        self.enter_text(self.full_name_input, full_name)

    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        self.enter_text(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        self.enter_text(self.password_input, password)

    @allure.step("Ввести повтор пароля")
    def enter_repeat_password(self, password: str):
        self.enter_text(self.repeat_password_input, password)

    @allure.step("Нажать 'Зарегистрироваться'")
    def click_register_button(self):
        self.click(self.register_button)

    @allure.step("Полная регистрация: {full_name}, {email}")
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    @allure.step("Ожидать редирект на логин")
    def wait_redirect_to_login_page(self):
        # Используем универсальный метод из BasePage
        self.wait_redirect_to("https://dev-cinescope.coconutqa.ru/login")

    @allure.step("Проверить уведомление о регистрации")
    def check_alert(self, text: str = "Подтвердите свою почту"):
        # Используем метод из BasePage с кастомным скриншотом
        super().check_alert(text, "registration_success")