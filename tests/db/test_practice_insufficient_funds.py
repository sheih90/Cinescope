import pytest
import logging
import random
from db_requester.db_helpers import DBHelper
from db_models.account import AccountTransactionTemplate

logger = logging.getLogger(__name__)


class TestInsufficientFunds:
    """
    Практическое задание:
    Проверка, что при недостатке средств транзакция откатывается
    и деньги остаются на местах
    """

    def test_insufficient_funds_rollback(self, db_helper: DBHelper):
        """
        Тест: Stan пытается перевести Bob'у больше, чем у него есть

        Ожидаемый результат:
        - Транзакция откатывается (rollback)
        - Балансы не изменились
        - Деньги остались на месте
        """
        logger.info("\n" + "=" * 80)
        logger.info("📚 ПРАКТИЧЕСКОЕ ЗАДАНИЕ: Недостаточно средств")
        logger.info("=" * 80)

        # ========== ПОДГОТОВКА ==========
        # Создаём уникальные имена пользователей
        stan_user = f"Stan_{random.randint(1, 10000)}"
        bob_user = f"Bob_{random.randint(1, 10000)}"

        # Создаём счета:
        # - У Stan: 1000 единиц
        # - У Bob: 500 единиц
        stan = db_helper.create_account(user=stan_user, balance=1000)
        bob = db_helper.create_account(user=bob_user, balance=500)

        # Сохраняем начальные балансы для проверки
        initial_stan_balance = stan.balance
        initial_bob_balance = bob.balance
        total_balance = initial_stan_balance + initial_bob_balance

        logger.info(f"📊 Начальные балансы:")
        logger.info(f"   Stan ({stan_user}): {initial_stan_balance}")
        logger.info(f"   Bob ({bob_user}): {initial_bob_balance}")
        logger.info(f"   Общая сумма: {total_balance}")

        # ========== ПРОВЕРКА ДО ТЕСТА ==========
        logger.info("\n🔍 Проверка начальных данных...")
        assert stan.balance == 1000, "Начальный баланс Stan неверный"
        assert bob.balance == 500, "Начальный баланс Bob неверный"
        logger.info("✅ Начальные балансы корректны")

        # ========== ПОПЫТКА ПЕРЕВОДА ==========
        # Stan пытается перевести Bob'у 1500 единиц
        # Но у Stan только 1000 - недостаточно!
        transfer_amount = 1500

        logger.info(f"\n💸 Попытка перевода: {transfer_amount} от Stan к Bob")
        logger.info(f"   ⚠️  У Stan только {stan.balance} - НЕДОСТАТОЧНО!")

        # Выполняем перевод в try-except для отлова ошибки
        try:
            db_helper.transfer_money(
                from_user=stan_user,
                to_user=bob_user,
                amount=transfer_amount
            )
            # Если дошли сюда - ошибка не произошла (этого не должно быть!)
            pytest.fail("Ожидалась ошибка ValueError, но её не было!")

        except ValueError as e:
            # Ожидаемая ошибка!
            logger.info(f"✅ Ошибка корректно выброшена: {e}")
            logger.info("✅ Транзакция прервана")

        # ========== ПРОВЕРКА ПОСЛЕ ПРОВАЛА ==========
        logger.info("\n🔍 Проверка балансов после неудачной транзакции...")

        # Получаем актуальные балансы из БД
        stan_after = db_helper.get_account_by_user(stan_user)
        bob_after = db_helper.get_account_by_user(bob_user)

        logger.info(f"📊 Балансы после попытки перевода:")
        logger.info(f"   Stan ({stan_user}): {stan_after.balance}")
        logger.info(f"   Bob ({bob_user}): {bob_after.balance}")

        # Проверяем, что балансы НЕ ИЗМЕНИЛИСЬ
        assert stan_after.balance == initial_stan_balance, \
            f"❌ Баланс Stan изменился! Было {initial_stan_balance}, стало {stan_after.balance}"

        assert bob_after.balance == initial_bob_balance, \
            f"❌ Баланс Bob изменился! Было {initial_bob_balance}, стало {bob_after.balance}"

        # Проверяем закон сохранения денег
        final_total = stan_after.balance + bob_after.balance
        assert final_total == total_balance, \
            f"❌ Общая сумма изменилась! Было {total_balance}, стало {final_total}"

        logger.info("✅ Баланс Stan не изменился (деньги на месте)")
        logger.info("✅ Баланс Bob не изменился")
        logger.info(f"✅ Общая сумма сохранена: {total_balance}")

        # ========== ФИНАЛЬНАЯ ПРОВЕРКА ==========
        logger.info("\n" + "=" * 80)
        logger.info("✅ ПРОВЕРКА ПРОЙДЕНА!")
        logger.info("=" * 80)
        logger.info("📋 Результаты:")
        logger.info("  1. ✅ Stan не смог перевести деньги (недостаточно средств)")
        logger.info("  2. ✅ Транзакция откатилась (rollback)")
        logger.info("  3. ✅ Балансы не изменились")
        logger.info("  4. ✅ Деньги остались на месте у каждого")
        logger.info("=" * 80)

        # ========== ОЧИСТКА ==========
        db_helper.delete_account(stan)
        db_helper.delete_account(bob)

        logger.info("\n🗑️ Тестовые данные удалены из БД")