import allure
from .page_action import PageAction


class BasePage(PageAction):
    """Базовый класс с общими элементами (шапка)"""

    HOME_BUTTON = "a[href='/' and text()='Cinescope']"
    ALL_MOVIES_BUTTON = "a[href='/movies' and text()='Все фильмы']"

    def __init__(self, page):
        super().__init__(page)

    @allure.step("Перейти на главную")
    def go_to_home_page(self):
        self.click(self.HOME_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/")

    @allure.step("Перейти в 'Все фильмы'")
    def go_to_all_movies(self):
        self.click(self.ALL_MOVIES_BUTTON)
        self.wait_for_url("https://dev-cinescope.coconutqa.ru/movies")