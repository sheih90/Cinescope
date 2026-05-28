from playwright.sync_api import Page
import time


def test_fill_registration_form(page: Page):
    # Переход на страницу
    page.goto("https://demoqa.com/webtables")

    # 1. Нажимаем кнопку Add
    page.click("button#addNewRecordButton")

    # ==========================================================
    # ПУНКТ 2: Ждем и убеждаемся, что форма открылась (is_visible)
    # ==========================================================
    # Ищем элемент, который содержит текст "Registration Form"
    modal_title = page.locator("#registration-form-modal")

    # Проверяем, что элемент виден (вернет True или False)
    is_form_visible = modal_title.is_visible()
    assert is_form_visible, "Модальное окно не открылось!"

    # ==========================================================
    # ПУНКТ 3: Заполняем First Name через плейсхолдер
    # ==========================================================
    # CSS-селектор: input у которого атрибут placeholder равен "First Name"
    first_name_input = page.locator('input[placeholder="First Name"]')
    first_name_input.fill("Дамир")

    # ==========================================================
    # ПУНКТ 4: Заполняем остальные поля
    # ==========================================================
    # Last Name
    page.locator('input[placeholder="Last Name"]').fill("QA Инженер")

    # Email (тут плейсхолдер "name@example.com")
    page.locator('input[placeholder="name@example.com"]').fill("damir@qa.ru")

    # Age
    page.locator('input[placeholder="Age"]').fill("25")

    # Salary
    page.locator('input[placeholder="Salary"]').fill("100000")

    # Department
    page.locator('input[placeholder="Department"]').fill("IT")

    # ==========================================================
    # ПУНКТ 5: Нажимаем кнопку Submit
    page.click("button#submit")

    # Проверка: убеждаемся, что новая запись появилась в таблице
    # Ждем, пока появится строка с нашим именем
    page.wait_for_selector("text=Дамир")

    print("Успешно! Новый пользователь добавлен в таблицу.")
    time.sleep(5)