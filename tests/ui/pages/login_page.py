import allure
from .base_page import BasePage


class CinescopeLoginPage(BasePage):
    """Страница входа"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']:has-text('Войти')"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

    @allure.step("Открыть страницу входа")
    def open(self):
        self.goto(self.url)

    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        self.fill(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        self.fill(self.password_input, password)

    @allure.step("Нажать 'Войти'")
    def click_login_button(self):
        self.click(self.login_button)

    @allure.step("Логин: {email}")
    def login(self, email: str, password: str):
        """Полный процесс входа"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    @allure.step("Ожидать главную страницу")
    def wait_redirect_to_home_page(self):
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/")
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/"

    @allure.step("Проверить уведомление: {text}")
    def check_alert(self, text: str = "Вы вошли в аккаунт"):
        notification = self.page.get_by_text(text)
        notification.wait_for(state="visible")
        self.take_screenshot("login_success")