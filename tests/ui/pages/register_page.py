import allure
from .base_page import BasePage


class CinescopeRegisterPage(BasePage):
    """Страница регистрации"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/register"

        # === ЛОКАТОРЫ СТРАНИЦЫ РЕГИСТРАЦИИ ===
        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"
        self.register_button = "button[type='submit']:has-text('Зарегистрироваться')"
        self.sign_button = "a[href='/login' and text()='Войти']"

    @allure.step("Открыть страницу регистрации")
    def open(self):
        """Переход на страницу регистрации"""
        self.goto(self.url)

    @allure.step("Ввести ФИО: {full_name}")
    def enter_full_name(self, full_name: str):
        """Ввод ФИО"""
        self.fill(self.full_name_input, full_name)

    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        """Ввод email"""
        self.fill(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        """Ввод пароля"""
        self.fill(self.password_input, password)

    @allure.step("Ввести подтверждение пароля")
    def enter_repeat_password(self, password: str):
        """Ввод подтверждения пароля"""
        self.fill(self.repeat_password_input, password)

    @allure.step("Нажать кнопку регистрации")
    def click_register_button(self):
        """Клик по кнопке регистрации"""
        self.click(self.register_button)

    @allure.step("Зарегистрировать пользователя: {full_name}, {email}")
    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        """Полный процесс регистрации"""
        self.enter_full_name(full_name)
        self.enter_email(email)
        self.enter_password(password)
        self.enter_repeat_password(confirm_password)
        self.click_register_button()

    @allure.step("Ожидать редирект на страницу логина")
    def wait_redirect_to_login_page(self):
        """Ожидание перехода на страницу логина"""
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/login")
        assert "/login" in self.page.url, f"Редирект на /login не произошел. URL: {self.page.url}"

    @allure.step("Проверить появление уведомления: {text}")
    def check_alert(self, text: str = "Подтвердите свою почту"):
        """Проверка всплывающего сообщения"""
        notification = self.page.get_by_text(text)
        notification.wait_for(state="visible")
        assert notification.is_visible(), f"Уведомление '{text}' не появилось"

        # Скриншот уведомления
        self.take_screenshot("registration_success_alert")

        notification.wait_for(state="hidden")
        assert not notification.is_visible(), f"Уведомление '{text}' не исчезло"