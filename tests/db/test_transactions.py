# tests/db/test_transactions.py
import pytest
import logging
import random
import allure
from sqlalchemy.orm import Session
from db_requester.db_helpers import DBHelper
from db_models.account import AccountTransactionTemplate
from utils.data_generator import DataGenerator

logger = logging.getLogger(__name__)


@allure.epic("Тестирование транзакций")
@allure.feature("Тестирование транзакций между счетами")
class TestMoneyTransfer:

    @allure.story("Корректность перевода денег между двумя счетами")
    @allure.description("""
    Этот тест проверяет корректность перевода денег между двумя счетами.

    Шаги:
    1. Создание двух счетов: отправитель и получатель.
    2. Фиксация начальных балансов.
    3. Выполнение перевода указанной суммы.
    4. Проверка изменения балансов.
    5. Проверка сохранения общей суммы в системе.
    6. Очистка тестовых данных.
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Damir")
    @allure.label("component", "financial_transactions")
    @allure.title("Успешный перевод 200 единиц между счетами")
    @allure.link("https://jira.example.com/PROJ-123", name="JIRA: PROJ-123")
    def test_money_transfer_success(self, db_helper: DBHelper):
        """
        Тест успешного перевода денег между счетами.
        Проверяет атомарность и целостность транзакции.
        """

        # ========== ПОДГОТОВКА ==========
        with allure.step("Подготовка тестовых данных: создание счетов"):
            sender_user = f"Sender_{random.randint(1, 10000)}"
            receiver_user = f"Receiver_{random.randint(1, 10000)}"

            sender = db_helper.create_account(user=sender_user, balance=1000)
            receiver = db_helper.create_account(user=receiver_user, balance=500)

            initial_total = sender.balance + receiver.balance

            allure.dynamic.parameter("sender", sender_user)
            allure.dynamic.parameter("receiver", receiver_user)
            allure.dynamic.parameter("initial_sender_balance", sender.balance)
            allure.dynamic.parameter("initial_receiver_balance", receiver.balance)
            allure.dynamic.parameter("transfer_amount", 200)

        # ========== ПРОВЕРКА ДО ==========
        with allure.step("Проверка начальных балансов"):
            assert sender.balance == 1000, "Начальный баланс отправителя неверный"
            assert receiver.balance == 500, "Начальный баланс получателя неверный"
            logger.info("Начальные балансы проверены")

        # ========== ПЕРЕВОД ==========
        transfer_amount = 200

        with allure.step(f"Выполнение перевода {transfer_amount} единиц"):
            db_helper.transfer_money(
                from_user=sender_user,
                to_user=receiver_user,
                amount=transfer_amount
            )

        # ========== ПРОВЕРКА ПОСЛЕ ==========
        with allure.step("Проверка балансов после перевода"):
            sender_after = db_helper.get_account_by_user(sender_user)
            receiver_after = db_helper.get_account_by_user(receiver_user)

            assert sender_after.balance == 800, \
                f"Ожидалось 800, но {sender_after.balance}"
            assert receiver_after.balance == 700, \
                f"Ожидалось 700, но {receiver_after.balance}"

            final_total = sender_after.balance + receiver_after.balance
            assert final_total == initial_total, \
                f"Сумма изменилась! Было {initial_total}, стало {final_total}"

            allure.dynamic.parameter("final_sender_balance", sender_after.balance)
            allure.dynamic.parameter("final_receiver_balance", receiver_after.balance)
            allure.dynamic.parameter("total_preserved", final_total == initial_total)

        # ========== ОЧИСТКА ==========
        with allure.step("Очистка тестовых данных"):
            db_helper.delete_account(sender)
            db_helper.delete_account(receiver)