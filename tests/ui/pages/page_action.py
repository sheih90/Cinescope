import allure
from playwright.sync_api import Page, Locator
from typing import Optional


class PageAction:
    """Базовый класс с общими действиями для всех страниц"""

    def __init__(self, page: Page):
        self.page = page

    @allure.step("Нажать на элемент: {locator}")
    def click(self, locator: str):
        """Клик по элементу"""
        self.page.locator(locator).click()

    @allure.step("Заполнить поле {locator} значение: {value}")
    def fill(self, locator: str, value: str):
        """Заполнение поля ввода"""
        self.page.locator(locator).fill(value)

    @allure.step("Ожидать видимости элемента: {locator}")
    def wait_for_visible(self, locator: str, timeout: int = 10000):
        """Ожидание видимости элемента"""
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)

    @allure.step("Ожидать исчезновения элемента: {locator}")
    def wait_for_hidden(self, locator: str, timeout: int = 10000):
        """Ожидание исчезновения элемента"""
        self.page.locator(locator).wait_for(state="hidden", timeout=timeout)

    @allure.step("Ожидать URL: {url}")
    def wait_for_url(self, url: str, timeout: int = 10000):
        """Ожидание перехода на URL"""
        self.page.wait_for_url(url, timeout=timeout)

    @allure.step("Перейти по URL: {url}")
    def goto(self, url: str):
        """Переход на страницу"""
        self.page.goto(url)

    @allure.step("Получить текст элемента: {locator}")
    def get_text(self, locator: str) -> str:
        """Получение текста элемента"""
        return self.page.locator(locator).inner_text()

    @allure.step("Проверить видимость элемента: {locator}")
    def is_visible(self, locator: str) -> bool:
        """Проверка видимости элемента"""
        return self.page.locator(locator).is_visible()

    @allure.step("Проверить существование элемента: {locator}")
    def is_element_present(self, locator: str) -> bool:
        """Проверка существования элемента на странице"""
        return self.page.locator(locator).count() > 0

    @allure.step("Сделать скриншот: {name}")
    def take_screenshot(self, name: str = "screenshot"):
        """Делает скриншот и прикрепляет его к Allure отчёту"""
        screenshot = self.page.screenshot()
        allure.attach(
            screenshot,
            name=name,
            attachment_type=allure.attachment_type.PNG
        )