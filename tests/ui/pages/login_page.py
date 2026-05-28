import allure
from .base_page import BasePage


class CinescopeLoginPage(BasePage):
    """Страница входа"""

    def __init__(self, page):
        super().__init__(page)
        self.url = "https://dev-cinescope.coconutqa.ru/login"

        # === ЛОКАТОРЫ СТРАНИЦЫ ЛОГИНА ===
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']:has-text('Войти')"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

    @allure.step("Открыть страницу входа")
    def open(self):
        """Переход на страницу входа"""
        self.goto(self.url)

    @allure.step("Ввести email: {email}")
    def enter_email(self, email: str):
        """Ввод email"""
        self.fill(self.email_input, email)

    @allure.step("Ввести пароль")
    def enter_password(self, password: str):
        """Ввод пароля"""
        self.fill(self.password_input, password)

    @allure.step("Нажать кнопку входа")
    def click_login_button(self):
        """Клик по кнопке входа"""
        self.click(self.login_button)

    @allure.step("Перейти на страницу регистрации")
    def click_register_link(self):
        """Переход на страницу регистрации"""
        self.click(self.register_button)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/register")

    @allure.step("Выполнить вход: {email}")
    def login(self, email: str, password: str):
        """Полный процесс входа"""
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    @allure.step("Ожидать редирект на главную страницу")
    def wait_redirect_to_home_page(self):
        """Ожидание перехода на главную страницу"""
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/")
        assert self.page.url == "https://dev-cinescope.coconutqa.ru/", \
            f"Редирект не произошел. URL: {self.page.url}"

    @allure.step("Проверить появление уведомления: {text}")
    def check_alert(self, text: str = "Вы вошли в аккаунт"):
        """Проверка всплывающего сообщения"""
        notification = self.page.get_by_text(text)
        notification.wait_for(state="visible")
        assert notification.is_visible(), f"Уведомление '{text}' не появилось"

        # Делаем скриншот ДО исчезновения уведомления!
        self.take_screenshot("success_alert")

        notification.wait_for(state="hidden")
        assert not notification.is_visible(), f"Уведомление '{text}' не исчезло"

    @allure.step("Проверить ошибку входа: {error_text}")
    def check_login_error(self, error_text: str = "Неверный email или пароль"):
        """Проверка ошибки входа"""
        error = self.page.get_by_text(error_text)
        error.wait_for(state="visible")
        assert error.is_visible(), f"Ошибка '{error_text}' не появилась"