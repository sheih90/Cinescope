import allure
from .base_page import BasePage


class MovieReviewPage(BasePage):
    """Страница фильма с отзывами"""

    def __init__(self, page):
        super().__init__(page)
        self.base_url = "https://dev-cinescope.coconutqa.ru/movies/"
        self.movie_id = ""

        # Локаторы
        self.review_textarea = "textarea[placeholder='Написать отзыв']"
        self.rating_button = "button[role='combobox']"
        self.submit_button = "button:has-text('Отправить')"

    @allure.step("Открыть страницу фильма: {movie_id}")
    def open_movie_page(self, movie_id: str):
        """Открытие страницы конкретного фильма"""
        self.movie_id = movie_id
        self.url = f"{self.base_url}{movie_id}"
        self.open()  # используем метод из BasePage

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
        self.assert_text_present(review_text)
        self.take_screenshot("review_submitted")