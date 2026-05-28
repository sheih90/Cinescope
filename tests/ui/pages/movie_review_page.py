import allure
from .base_page import BasePage


class MovieReviewPage(BasePage):
    """Страница фильма с возможностью оставить отзыв"""

    def __init__(self, page):
        super().__init__(page)
        # URL будет динамическим, поэтому базовый адрес
        self.base_url = "https://dev-cinescope.coconutqa.ru/movies/"

        # === ЛОКАТОРЫ ===
        # Поле для текста отзыва (textarea с placeholder "Написать отзыв")
        self.review_textarea = "textarea[placeholder='Написать отзыв']"

        # Поле для оценки (input type="number" рядом с текстом "Оценка:")
        # Используем label + input
        self.rating_input = "input[type='number']"

        # Кнопка "Отправить"
        self.submit_button = "button:has-text('Отправить')"

        # Секция с существующими отзывами (если появятся)
        self.reviews_section = "div:has-text('Отзывы:')"

    @allure.step("Открыть страницу фильма {movie_id}")
    def open_movie_page(self, movie_id: str):
        """Переход на страницу конкретного фильма"""
        self.goto(f"{self.base_url}{movie_id}")

    @allure.step("Ввести текст отзыва: {text}")
    def write_review_text(self, text: str):
        """Ввод текста в поле отзыва"""
        self.fill(self.review_textarea, text)

    @allure.step("Установить оценку: {rating}")
    def set_rating(self, rating: int):
        """Установка оценки через кастомный выпадающий список"""

        # 1. Находим кнопку с текущим рейтингом (где написано "5")
        # Ищем кнопку с ролью combobox
        rating_button = self.page.locator("button[role='combobox']")

        # 2. Кликаем по ней, чтобы открыть список
        rating_button.click()

        # 3. Выбираем нужную оценку из списка (например, 4 или 5)
        # Ищем элемент с текстом нужной цифры
        rating_option = self.page.locator(f"div[role='option'] >> text={rating}")
        rating_option.click()

    @allure.step("Отправить отзыв")
    def submit_review(self):
        """Нажатие кнопки Отправить"""
        self.click(self.submit_button)

    @allure.step("Полный процесс: оставить отзыв '{text}' с оценкой {rating}")
    def leave_review(self, text: str, rating: int):
        """Комплексный метод для оставления отзыва"""
        self.write_review_text(text)
        self.set_rating(rating)
        self.submit_review()

    @allure.step("Проверить появление отзыва в списке")
    def check_review_appeared(self, review_text: str):
        """Проверка, что отзыв появился на странице"""
        # Ждём появления текста отзыва в секции отзывов
        review_locator = self.page.locator(f"text={review_text}")
        review_locator.wait_for(state="visible", timeout=10000)

        assert review_locator.is_visible(), f"Отзыв '{review_text}' не появился на странице"

        # Скриншот результата
        self.take_screenshot("review_submitted")