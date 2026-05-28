import allure
from .base_page import BasePage


class MovieReviewPage(BasePage):
    """Страница фильма с отзывами"""

    def __init__(self, page):
        super().__init__(page)
        self.base_url = "https://dev-cinescope.coconutqa.ru/movies/"

        # === ЛОКАТОРЫ ===
        self.review_textarea = "textarea[placeholder='Написать отзыв']"
        self.rating_button = "button[role='combobox']"
        self.submit_button = "button:has-text('Отправить')"

    @allure.step("Открыть страницу фильма: {movie_id}")
    def open_movie_page(self, movie_id: str):
        self.goto(f"{self.base_url}{movie_id}")

    @allure.step("Ввести текст отзыва: {text}")
    def write_review_text(self, text: str):
        self.fill(self.review_textarea, text)

    @allure.step("Выбрать оценку: {rating}")
    def set_rating(self, rating: int):
        """Выбор оценки из выпадающего списка"""
        self.click(self.rating_button)

        # Кликаем по нужной цифре в списке
        rating_option = self.page.locator(f"div[role='option'] >> text={rating}")
        rating_option.click()

    @allure.step("Отправить отзыв")
    def submit_review(self):
        self.click(self.submit_button)

    @allure.step("Оставить отзыв: '{text}', оценка: {rating}")
    def leave_review(self, text: str, rating: int):
        """Бизнес-метод: полный процесс оставления отзыва"""
        self.write_review_text(text)
        self.set_rating(rating)
        self.submit_review()

    @allure.step("Проверить появление отзыва")
    def check_review_appeared(self, review_text: str):
        """Проверка, что отзыв появился"""

        # Ждём появления текста на странице
        self.page.get_by_text(review_text).wait_for(state="visible", timeout=10000)

        self.take_screenshot("review_submitted")