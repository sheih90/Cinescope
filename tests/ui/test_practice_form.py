from playwright.sync_api import Page
import time
from pathlib import Path
from datetime import datetime

def test_fill_practice_form(page: Page):
    page.goto("https://demoqa.com/automation-practice-form")
    form_title = page.get_by_text("Student Registration Form")
    is_form_visible = form_title.is_visible()
    assert is_form_visible, "Форма не открылась!"
    # Получаем текущую дату
    today = datetime.now()
    # Форматируем её под стиль сайта (День СокрМесяц Год)
    # Пример: 25 May 2026
    expected_default_date = today.strftime("%d %b %Y")
    # Получаем значение из атрибута value у инпута
    # ВАЖНО: у input нет inner_text, у него есть атрибут value!
    date_input = page.locator("#dateOfBirthInput")
    actual_default_date = date_input.get_attribute("value")

    # 4. Делаем ассерт
    assert actual_default_date == expected_default_date, f"Дата не совпала! Ожидалось: {expected_default_date}, Было: {actual_default_date}"
    print(f"✅ Дата по умолчанию верна: {actual_default_date}")
    first_name_input = page.locator('input[id="firstName"]')
    last_name_input = page.locator('input[id="lastName"]')
    email_input = page.locator('input[id="userEmail"]')
    user_number_input = page.locator('input[placeholder="Mobile Number"]')
    current_address_input = page.locator('#currentAddress')

    first_name_input.fill("DTest")
    last_name_input.fill("DTestovyi")
    email_input.fill("dtest@t.ru")
    page.get_by_role("radio", name="Male", exact=True).check()
    user_number_input.fill("9876543210")
    page.click("#dateOfBirthInput")
    page.fill("#dateOfBirthInput", "20 Jun 1990")
    page.click("#subjectsInput")
    page.type("#subjectsInput", "h")
    page.click("text=History")
    page.type("#subjectsInput", "a")
    page.click("text=Arts")
    page.check("#hobbies-checkbox-3")
    # === ЗАГРУЗКА ФАЙЛА ===
    # Строим путь от корня проекта
    project_root = Path(__file__).parent.parent.parent
    file_path = project_root / "files" / "test_files" / "360 - Buttons.png"

    page.set_input_files("#uploadPicture", str(file_path))
    current_address_input.fill("г. Москва, ул. Тестовая, д. 1, кв. 42")
    page.click("#state")
    page.click("text=NCR")
    page.click("#city")
    page.click("text=Noida")
    page.click("#submit")
    # === Проверка результата ===
    # После отправки появляется модальное окно с сообщением об успехе
    page.wait_for_selector("text=Thanks for submitting the form")
    assert page.inner_text("table")  # Проверяем, что таблица с данными существует

    # Получаем весь текст из футера
    footer_text = page.inner_text("footer")
    # Текст, который ожидаем увидеть
    expected_footer = "© 2013-2026 TOOLSQA.COM | ALL RIGHTS RESERVED."
    # Ассерт (проверяем, что ожидаемый текст находится ВНУТРИ полученного)
    # Используем 'in', потому что в footer_text могут быть лишние пробелы или переносы строк
    assert expected_footer in footer_text, "Текст в футере не совпадает!"

    print("✅ Текст в футере верный!")

    print("✅ Форма успешно отправлена! Тест пройден.")

    time.sleep(5)

