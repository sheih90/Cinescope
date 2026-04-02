import pytest
import json
import logging
from entities.product_model import Product, ProductCategory

logger = logging.getLogger(__name__)


class TestProductModel:
    """Тесты модели Product"""

    def test_create_product(self):
        """1. Создание продукта"""
        product = Product(
            name="Ноутбук",
            price=75000.50,
            in_stock=True,
            category=ProductCategory.ELECTRONICS
        )

        assert product.name == "Ноутбук"
        assert product.price == 75000.50
        assert product.in_stock == True
        assert product.category == ProductCategory.ELECTRONICS

        logger.info(f"✓ Продукт создан: {product}")

    def test_serialize_to_json(self):
        """2. Сериализация в JSON"""
        product = Product(
            name="Футболка",
            price=1500.0,
            in_stock=True,
            category=ProductCategory.CLOTHING
        )

        # Сериализация в JSON строку
        json_str = product.model_dump_json()

        logger.info("Сериализация в JSON:")
        logger.info(json_str)

        # Проверяем, что это валидный JSON
        parsed = json.loads(json_str)
        assert parsed["name"] == "Футболка"
        assert parsed["price"] == 1500.0
        assert parsed["in_stock"] == True
        assert parsed["category"] == "Одежда"

    def test_deserialize_from_json(self):
        """3. Десериализация из JSON"""
        json_data = """
        {
            "name": "Python. Путь к мастерству",
            "price": 2500.0,
            "in_stock": true,
            "category": "Книги"
        }
        """

        # Десериализация из JSON строки
        product = Product.model_validate_json(json_data)

        logger.info("Десериализация из JSON:")
        logger.info(f"  name: {product.name}")
        logger.info(f"  price: {product.price}")
        logger.info(f"  in_stock: {product.in_stock}")
        logger.info(f"  category: {product.category}")

        assert product.name == "Python. Путь к мастерству"
        assert product.price == 2500.0
        assert product.in_stock == True
        assert product.category == ProductCategory.BOOKS

    def test_full_cycle(self):
        """4. Полный цикл: создание → сериализация → десериализация → вывод"""
        logger.info("=" * 80)
        logger.info("ПОЛНЫЙ ЦИКЛ РАБОТЫ С МОДЕЛЬЮ")
        logger.info("=" * 80)

        # 1. Создаём объект
        original_product = Product(
            name="Смартфон",
            price=45000.0,
            in_stock=True,
            category=ProductCategory.ELECTRONICS
        )

        logger.info("\nИсходный объект:")
        logger.info(f"   {original_product}")
        logger.info(f"   Category: {original_product.category.value}")

        # 2. Сериализуем в JSON
        json_str = original_product.model_dump_json()

        logger.info("\nJSON представление:")
        logger.info(f"   {json_str}")

        # 3. Десериализуем обратно
        restored_product = Product.model_validate_json(json_str)

        logger.info("\nВосстановленный объект:")
        logger.info(f"   {restored_product}")

        # 4. Проверяем, что объекты равны
        logger.info("\nПроверка целостности:")
        assert original_product.name == restored_product.name
        assert original_product.price == restored_product.price
        assert original_product.in_stock == restored_product.in_stock
        assert original_product.category == restored_product.category

        logger.info("Все поля совпадают!")
        logger.info("=" * 80)

    def test_validation_errors(self):
        """Тест валидации (отрицательная цена)"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Product(
                name="Товар",
                price=-100,  # Отрицательная цена
                in_stock=True
            )
