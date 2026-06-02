from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Product:
    sku: str
    name: str
    price: float
    quantity: int = 0

    def is_in_stock(self) -> bool:
        return self.quantity > 0

    def __str__(self):
        return f"[{self.sku}] {self.name} — ${self.price:.2f} ({self.quantity} in stock)"


class Inventory:
    """
    In-memory product inventory with add, remove, search, and low-stock reporting.
    """

    LOW_STOCK_THRESHOLD = 5

    def __init__(self):
        self._products: dict[str, Product] = {}

    def add_product(self, sku: str, name: str, price: float, quantity: int = 0) -> Product:
        if sku in self._products:
            raise ValueError(f"Product with SKU '{sku}' already exists")
        product = Product(sku=sku, name=name, price=price, quantity=quantity)
        self._products[sku] = product
        return product

    def restock(self, sku: str, amount: int) -> Product:
        product = self._get_or_raise(sku)
        if amount <= 0:
            raise ValueError("Restock amount must be positive")
        product.quantity += amount
        return product

    def sell(self, sku: str, quantity: int = 1) -> Product:
        product = self._get_or_raise(sku)
        if product.quantity < quantity:
            raise ValueError(f"Not enough stock for '{sku}' (have {product.quantity}, need {quantity})")
        product.quantity -= quantity
        return product

    def search(self, query: str) -> list[Product]:
        query_lower = query.lower()
        return [
            p for p in self._products.values()
            if query_lower in p.name.lower() or query_lower in p.sku.lower()
        ]

    def low_stock(self) -> list[Product]:
        return [p for p in self._products.values() if p.quantity <= self.LOW_STOCK_THRESHOLD]

    def all_products(self) -> list[Product]:
        return list(self._products.values())

    def get(self, sku: str) -> Optional[Product]:
        return self._products.get(sku)

    def remove_product(self, sku: str) -> None:
        self._get_or_raise(sku)
        del self._products[sku]

    def total_value(self) -> float:
        return sum(p.price * p.quantity for p in self._products.values())

    def _get_or_raise(self, sku: str) -> Product:
        product = self._products.get(sku)
        if product is None:
            raise KeyError(f"No product with SKU '{sku}'")
        return product
