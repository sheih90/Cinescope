import allure
from .base_page import BasePage


class CinescopeRegisterPage(BasePage):
    """Страница регистрации"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # === ЛОКАТОРЫ ===
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"
        self.register_button = "button[type='submit']:has-text('Зарегистрироваться')"

    @allure.step("Открыть страницу регистрации")
    def open(self):
        self.goto(self.url)

    @allure.step("Ввести ФИО: {full_name}")
    def enter_full_name(self, full_name: str):
        self.fill(self.full_name_input, full_name)

    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        self.fill(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        self.fill(self.password_input, password)

    @allure.step("Ввести повтор пароля")
    def enter_repeat_password(self, password: str):
        self.fill(self.repeat_password_input, password)

    @allure.step("Нажать 'Зарегистрироваться'")
    def click_register_button(self):
        self.click(self.register_button)

    @allure.step("Полная регистрация: {full_name}, {email}")
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Бизнес-метод: заполняет и отправляет форму"""
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    @allure.step("Ожидать редирект на логин")
    def wait_redirect_to_login_page(self):
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/login")
        assert "/login" in self.page.url, "Редирект на /login не произошел"

    @allure.step("Проверить уведомление: {text}")
    def check_alert(self, text: str = "Подтвердите свою почту"):
        """Проверка алерта + скриншот"""
        notification = self.page.get_by_text(text)
        notification.wait_for(state="visible")

        self.take_screenshot("registration_success")

        notification.wait_for(state="hidden")