import allure
from .page_action import PageAction


class BasePage(PageAction):
    """Базовый класс с общими элементами (шапка)"""

    HOME_BUTTON = "a[href='/' and text()='Cinescope']"
    ALL_MOVIES_BUTTON = "a[href='/movies' and text()='Все фильмы']"

    def __init__(self, page):
        super().__init__(page)
        self.url = ""  # Будет переопределен в дочерних классах

    @allure.step("Открыть страницу")
    def open(self):
        """Универсальный метод открытия страницы"""
        self.goto(self.url)

    @allure.step("Перейти на главную")
    def go_to_home_page(self):
        self.click(self.HOME_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    @allure.step("Перейти в 'Все фильмы'")
    def go_to_all_movies(self):
        self.click(self.ALL_MOVIES_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    @allure.step("Ожидать URL: {url}")
    def wait_redirect_to(self, url: str):
        """Универсальный метод ожидания редиректа"""
        self.wait_for_url(url)
        self.assert_url(url)

    @allure.step("Проверить уведомление: {text}")
    def check_alert(self, text: str, screenshot_name: str = "alert"):
        """Универсальный метод проверки уведомления"""
        notification = self.page.get_by_text(text)
        notification.wait_for(state="visible")
        self.assert_text_present(text)
        self.take_screenshot(screenshot_name)