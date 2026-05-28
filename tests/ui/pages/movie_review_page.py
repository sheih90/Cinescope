import allure
from .base_page import BasePage


class MovieReviewPage(BasePage):
    """Страница фильма с отзывами"""

    def __init__(self, page):
        super().__init__(page)
        self.base_url = "https://dev-cinescope.coconutqa.ru/movies/"

        # Локаторы
        self.review_textarea = "textarea[placeholder='Написать отзыв']"
        self.rating_button = "button[role='combobox']"
        self.submit_button = "button:has-text('Отправить')"

    @allure.step("Открыть страницу фильма: {movie_id}")
    def open_movie_page(self, movie_id: str):
        self.goto(f"{self.base_url}{movie_id}")

    @allure.step("Ввести текст отзыва: {text}")
    def write_review_text(self, text: str):
        self.enter_text(self.review_textarea, text)

    @allure.step("Выбрать оценку: {rating}")
    def set_rating(self, rating: int):
        self.click(self.rating_button)
        rating_option = self.page.locator(f"div[role='option'] >> text={rating}")
        rating_option.click()

    @allure.step("Отправить отзыв")
    def submit_review(self):
        self.click(self.submit_button)

    @allure.step("Оставить отзыв: '{text}', оценка: {rating}")
    def leave_review(self, text: str, rating: int):
        self.write_review_text(text)
        self.set_rating(rating)
        self.submit_review()

    @allure.step("Проверить появление отзыва")
    def check_review_appeared(self, review_text: str):
        """Проверка, что отзыв появился"""
        # Используем базовый метод проверки текста
        self.assert_text_present(review_text)
        self.take_screenshot("review_submitted")