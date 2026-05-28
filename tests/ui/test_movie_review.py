import allure
import pytest
from playwright.sync_api import Page
from .pages.register_page import CinescopeRegisterPage
from .pages.login_page import CinescopeLoginPage
from .pages.movie_review_page import MovieReviewPage
from random import randint, choice


@allure.feature("Отзывы")
@allure.story("Оставление отзыва под фильмом")
class TestMovieReview:

    @allure.title("Полный цикл: Регистрация -> Вход -> Отзыв")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_leave_review_full_cycle(self, page: Page):
        """
        Тест проверяет полный путь пользователя:
        1. Регистрация
        2. Вход в систему
        3. Переход к фильму
        4. Оставление отзыва
        """

        # === 1. Подготовка данных ===
        email = f"reviewer_{randint(1000, 9999)}@test.ru"
        password = "Test@1234"
        first_names = ["Александр", "Дмитрий", "Максим"]
        last_names = ["Иванов", "Петров", "Сидоров"]
        full_name = f"{choice(first_names)} {choice(last_names)}"
        movie_id = "51251"  # ID фильма со скриншота

        # === 2. Регистрация ===
        with allure.step("Регистрация нового пользователя"):
            register_page = CinescopeRegisterPage(page)
            register_page.open()
            register_page.register(full_name, email, password, password)
            register_page.wait_redirect_to_login_page()

        # === 3. Вход в систему (Login) ===
        with allure.step("Авторизация пользователя"):
            # После регистрации мы уже на странице логина
            login_page = CinescopeLoginPage(page)
            login_page.login(email, password)
            login_page.wait_redirect_to_home_page()  # Убеждаемся, что вошли успешно

        # === 4. Переход к фильму ===
        with allure.step(f"Переход на страницу фильма {movie_id}"):
            review_page = MovieReviewPage(page)
            review_page.open_movie_page(movie_id)

        # === 5. Оставление отзыва ===
        review_text = f"Отличный фильм! Спасибо автору. (Пользователь: {full_name})"
        rating = 5

        with allure.step(f"Написание отзыва: '{review_text}'"):
            review_page.write_review_text(review_text)
            review_page.set_rating(rating)

        with allure.step("Отправка отзыва"):
            review_page.submit_review()

        with allure.step("Проверка появления отзыва"):
            review_page.check_review_appeared(review_text)

        print(f"✅ Отзыв успешно оставлен пользователем {email}!")