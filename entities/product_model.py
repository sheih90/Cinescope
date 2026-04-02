from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProductCategory(str, Enum):
    """Категории продуктов (Enum)"""
    ELECTRONICS = "Электроника"
    CLOTHING = "Одежда"
    FOOD = "Продукты"
    BOOKS = "Книги"


class Product(BaseModel):
    """
    Модель данных для продукта.
    """
    name: str
    price: float = Field(..., ge=0, description="Цена должна быть >= 0")
    in_stock: bool
    category: Optional[ProductCategory] = None  # Усложнённая версия

    def __str__(self) -> str:
        """Красивое строковое представление"""
        status = "в наличии" if self.in_stock else "нет в наличии"
        return f"Product(name={self.name}, price={self.price}₽, {status})"