import allure
from playwright.sync_api import Page
import os
from datetime import datetime


class PageAction:
    """Базовый класс с минимальными общими действиями"""

    def __init__(self, page: Page):
        self.page = page

    @allure.step("Перейти на страницу: {url}")
    def goto(self, url: str):
        """Переход на URL"""
        self.page.goto(url)

    @allure.step("Клик: {locator}")
    def click(self, locator: str):
        """Клик по элементу"""
        self.page.locator(locator).click()

    @allure.step("Ввод текста: {locator} = {value}")
    def fill(self, locator: str, value: str):
        """Ввод текста в поле"""
        self.page.locator(locator).fill(value)

    @allure.step("Ожидание видимости: {locator}")
    def wait_for_visible(self, locator: str, timeout: int = 10000):
        """Ожидание видимости элемента"""
        self.page.locator(locator).wait_for(state="visible", timeout=timeout)

    @allure.step("Ожидание URL: {url}")
    def wait_for_url(self, url: str, timeout: int = 10000):
        """Ожидание перехода на URL"""
        self.page.wait_for_url(url, timeout=timeout)

    @allure.step("Скриншот: {name}")
    def take_screenshot(self, name: str = "screenshot"):
        """Скриншот с сохранением в папку и в Allure"""
        screenshot_dir = "tests/screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(screenshot_dir, f"{name}_{timestamp}.png")

        screenshot = self.page.screenshot()
        with open(filepath, "wb") as f:
            f.write(screenshot)

        allure.attach(screenshot, name=name, attachment_type=allure.attachment_type.PNG)