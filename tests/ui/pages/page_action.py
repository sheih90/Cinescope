import allure
from playwright.sync_api import Page, expect
import os
from datetime import datetime


class PageAction:
    """Базовый класс с общими действиями"""

    def __init__(self, page: Page):
        self.page = page

    # ===== БАЗОВЫЕ ДЕЙСТВИЯ =====

    @allure.step("Перейти на страницу: {url}")
    def goto(self, url: str):
        self.page.goto(url)

    @allure.step("Клик: {locator}")
    def click(self, locator: str):
        self.page.locator(locator).click()

    @allure.step("Ввод текста: {locator} = {value}")
    def fill(self, locator: str, value: str):
        self.page.locator(locator).fill(value)

    @allure.step("Ожидание видимости: {locator}")
    def wait_for_visible(self, locator: str, timeout: int = 10000):
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)

    @allure.step("Ожидание URL: {url}")
    def wait_for_url(self, url: str, timeout: int = 10000):
        self.page.wait_for_url(url, timeout=timeout)

    # ===== УНИВЕРСАЛЬНЫЕ МЕТОДЫ ВВОДА =====

    @allure.step("Ввести текст в поле: {locator}")
    def enter_text(self, locator: str, text: str):
        """Универсальный метод ввода текста"""
        self.page.locator(locator).fill(text)

    @allure.step("Очистить поле: {locator}")
    def clear_field(self, locator: str):
        self.page.locator(locator).clear()

    # ===== УНИВЕРСАЛЬНЫЕ ПРОВЕРКИ =====

    @allure.step("Проверить видимость: {locator}")
    def assert_element_visible(self, locator: str, message: str = "Элемент не виден"):
        """Проверка видимости элемента"""
        element = self.page.locator(locator)
        element.wait_for(state="visible", timeout=10000)
        assert element.is_visible(), message

    @allure.step("Проверить текст: {text}")
    def assert_text_present(self, text: str, message: str = "Текст не найден"):
        """Проверка наличия текста"""
        locator = self.page.get_by_text(text)
        locator.wait_for(state="visible", timeout=10000)
        assert locator.is_visible(), message

    @allure.step("Проверить URL: {expected_url}")
    def assert_url(self, expected_url: str):
        """Проверка текущего URL"""
        # Playwright support exact URL match
        expect(self.page).to_have_url(expected_url, timeout=10000)

    @allure.step("Проверить значение поля: {locator}")
    def assert_field_value(self, locator: str, expected_value: str):
        """Проверка значения поля"""
        expect(self.page.locator(locator)).to_have_value(expected_value, timeout=10000)

    # ===== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ =====

    @allure.step("Получить текст: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).inner_text()

    @allure.step("Скриншот: {name}")
    def take_screenshot(self, name: str = "screenshot"):
        screenshot_dir = "tests/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")

        screenshot = self.page.screenshot()
        with open(filepath, "wb") as f:
            f.write(screenshot)

        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)