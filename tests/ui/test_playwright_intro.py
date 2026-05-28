from playwright.sync_api import Page, expect, Playwright, sync_playwright
from random import randint
import time


def test_first_playwright_run(page):  # <--- Принимаем фикстуру page как аргумент
    # Pytest сам найдет функцию page() в conftest.py, запустит браузер и даст объект page

    # 1. Переходим на сайт
    url = "https://dev-cinescope.coconutqa.ru/"
    page.goto(url)

    # 2. Проверяем заголовок (простая проверка)
    assert "Cinescope" in page.title()


def test_text_box(page: Page):
    page.goto('https://demoqa.com/text-box')

    page.fill(selector='#userName', value='testQa')
    page.fill(selector='#userEmail', value='testQa@tast.com')
    page.fill(selector='#currentAddress', value='Test country')
    page.fill(selector='#permanentAddress', value='Test street')
    page.locator('#submit').click()

    time.sleep(10)

    expect(page.locator('#output #name')).to_have_text('Name:testQa')
    expect(page.locator('#output #email')).to_have_text('Email:testQa@tast.com')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :Test country')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :Test street')


def test_text_box_register(page: Page):
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    # вариант №1
    username_locator = '[name="fullName"]'
    email_loacor = '[name="email"]'
    password_locator = '[name="password"]'
    repeat_password_locator = '[name="passwordRepeat"]'

    user_email = f'test_{randint(1, 9999)}@email.qa'

    # page.pause()

    page.fill(username_locator, 'Тестовый Тест Тестович')
    page.fill(email_loacor, user_email)
    page.fill(password_locator, 'qwerty123Q')
    page.fill(repeat_password_locator, 'qwerty123Q')

    page.click('button[type="submit"]')

    page.wait_for_url('https://dev-cinescope.coconutqa.ru/login')
    expect(page.get_by_text("Подтвердите свою почту")).to_be_visible(visible=True)


def test_run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://demoqa.com/")
    page.get_by_role("link", name="Elements").click()
    page.get_by_role("link", name="Text Box").click()
    page.get_by_role("textbox", name="Full Name").click()
    page.get_by_role("textbox", name="Full Name").fill("ТЕст")
    page.get_by_role("textbox", name="Full Name").press("Tab")
    page.get_by_role("textbox", name="name@example.com").fill("test@t.ru")
    page.get_by_role("textbox", name="name@example.com").press("Tab")
    page.get_by_role("textbox", name="Current Address").fill("testCurrentTExt")
    page.get_by_role("textbox", name="Current Address").press("Tab")
    page.locator("#permanentAddress").fill("testPermanentText")
    page.get_by_role("button", name="Submit").click()

    expect(page.locator('#output #name')).to_have_text('Name:ТЕст')
    expect(page.locator('#output #email')).to_have_text('Email:test@t.ru')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :testCurrentTExt')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :testPermanentText')

    # ---------------------
    context.close()
    browser.close()






