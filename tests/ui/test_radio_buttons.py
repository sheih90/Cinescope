from playwright.sync_api import Page


def test_radio_buttons_state(page: Page):
    # 1. Переходим на страницу
    page.goto("https://demoqa.com/radio-button")

    # === ЛОКАТОРЫ ===
    # Используем ID, они уникальны и надежны
    btn_yes = page.locator("#yesRadio")
    btn_impressive = page.locator("#impressiveRadio")
    btn_no = page.locator("#noRadio")

    # === ПРОВЕРКА АКТИВНОСТИ ===

    # 1. Проверяем, что кнопка YES активна (enabled)
    assert btn_yes.is_enabled() is True, "Кнопка 'Yes' должна быть активна!"

    # 2. Проверяем, что кнопка IMPRESSIVE активна (enabled)
    assert btn_impressive.is_enabled() is True, "Кнопка 'Impressive' должна быть активна!"

    # 3. Проверяем, что кнопка NO НЕ активна (disabled)
    # Метод is_disabled() возвращает True, если элемент заблокирован
    assert btn_no.is_disabled() is True, "Кнопка 'No' должна быть неактивна!"

    print("✅ Все проверки активности радиокнопок пройдены успешно!")