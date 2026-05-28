import pytest
from playwright.sync_api import sync_playwright

from tests.ui.tools import Tools

# Таймаут по умолчанию (30 секунд)
DEFAULT_UI_TIMEOUT = 30000


@pytest.fixture(scope="session")
def browser():
    # Запускаем Playwright один раз на всю сессию тестов
    pw = sync_playwright().start()

    # Запускаем браузер
    # headless=False поставь, если хочешь видеть браузер при прогоне тестов
    # headless=True - браузер работает в фоне (быстрее)
    browser_instance = pw.chromium.launch(headless=False)

    yield browser_instance  # Отдаем браузер тестам

    # После всех тестов закрываем всё
    browser_instance.close()
    pw.stop()


@pytest.fixture(scope="function")
def context(browser):
    context_instance = browser.new_context()

    # Включаем трассировку
    context_instance.tracing.start(
        screenshots=True,  # Скриншоты на каждом шаге
        snapshots=True,  # HTML снимки
        sources=True  # Исходный код теста
    )
    context_instance.set_default_timeout(DEFAULT_UI_TIMEOUT)

    yield context_instance

    # Останавливаем трассировку и сохраняем
    timestamp = Tools.get_timestamp()
    trace_path = Tools.files_dir("playwright_trace", f"trace_{timestamp}.zip")

    context_instance.tracing.stop(path=trace_path)
    context_instance.close()


@pytest.fixture(scope="function")
def page(context):
    # Для каждого теста создаем чистую страницу
    page_instance = context.new_page()

    yield page_instance

    page_instance.close()