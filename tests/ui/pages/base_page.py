import allure
from .page_action import PageAction


class BasePage(PageAction):
    """Базовый класс для всех страниц с общими элементами"""

    # === ОБЩИЕ ЛОКАТОРЫ (ШАПКА) ===
    HOME_BUTTON = "a[href='/' and text()='Cinescope']"
    ALL_MOVIES_BUTTON = "a[href='/movies' and text()='Все фильмы']"

    def __init__(self, page):
        super().__init__(page)

    @allure.step("Перейти на главную страницу")
    def go_to_home_page(self):
        """Переход на главную страницу"""
        self.click(self.HOME_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    @allure.step("Перейти на страницу 'Все фильмы'")
    def go_to_all_movies(self):
        """Переход на страницу всех фильмов"""
        self.click(self.ALL_MOVIES_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")

    @allure.step("Проверить заголовок страницы")
    def get_page_title(self) -> str:
        """Получить заголовок страницы"""
        return self.page.title()