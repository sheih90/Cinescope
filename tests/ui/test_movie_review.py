import allure
import pytest
from playwright.sync_api import Page
from tests.ui.pages.register_page import CinescopeRegisterPage
from tests.ui.pages.login_page import CinescopeLoginPage
from tests.ui.pages.movie_review_page import MovieReviewPage
from random import randint, choice


@allure.feature("Отзывы")
@allure.story("Оставление отзыва под фильмом")
class TestMovieReview:
    # Список ID фильмов для тестирования
    MOVIE_IDS = ["51212", "51042", "51226", "51213", "51054", "51211", "50932"]

    @allure.title("Оставить отзыв на случайном фильме")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_leave_review_on_random_movie(self, page: Page):
        """
        Тест проверяет оставление отзыва на случайном фильме
        """

        # === 1. Подготовка данных ===
        email = f"reviewer_{randint(1000, 9999)}@test.ru"
        password = "Test@1234"
        first_names = ["Александр", "Дмитрий", "Максим", "Анна", "Мария"]
        last_names = ["Иванов", "Петров", "Сидоров", "Смирнова", "Попова"]
        full_name = f"{choice(first_names)} {choice(last_names)}"

        # Выбираем случайный фильм
        movie_id = choice(self.MOVIE_IDS)

        with allure.step("Регистрация нового пользователя"):
            register_page = CinescopeRegisterPage(page)
            register_page.open()
            register_page.register(full_name, email, password, password)
            register_page.wait_redirect_to_login_page()

        with allure.step("Авторизация пользователя"):
            login_page = CinescopeLoginPage(page)
            login_page.login(email, password)
            login_page.wait_redirect_to_home_page()

        with allure.step(f"Переход на страницу фильма {movie_id}"):
            review_page = MovieReviewPage(page)
            review_page.open_movie_page(movie_id)

        # === 5. Оставление отзыва ===
        review_text = f"Отличный фильм! Рекомендую к просмотру. (Тест: {full_name})"
        rating = choice([4, 5])  # Хорошие оценки

        with allure.step(f"Написание отзыва: '{review_text}'"):
            review_page.write_review_text(review_text)
            review_page.set_rating(rating)

        with allure.step("Отправка отзыва"):
            review_page.submit_review()

        with allure.step("Проверка появления отзыва"):
            review_page.check_review_appeared(review_text)

        print(f"✅ Отзыв оставлен на фильме {movie_id} пользователем {email}!")