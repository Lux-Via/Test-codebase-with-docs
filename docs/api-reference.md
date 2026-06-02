# API Reference

## calculator.py

### `OperationResult`
A dataclass returned by every calculation, stored in history.

| Field | Type | Description |
|---|---|---|
| `operation` | str | Operator symbol (`+`, `-`, `*`, `/`, `**`, `sqrt`) |
| `a` | float | First operand |
| `b` | float or None | Second operand (None for unary ops like sqrt) |
| `result` | float | Computed result |

### `Calculator`
Stateful calculator that records every operation.

| Method | Parameters | Returns | Notes |
|---|---|---|---|
| `add(a, b)` | float, float | float | — |
| `subtract(a, b)` | float, float | float | — |
| `multiply(a, b)` | float, float | float | — |
| `divide(a, b)` | float, float | float | raises `ValueError` if b=0 |
| `power(base, exponent)` | float, float | float | — |
| `sqrt(a)` | float | float | raises `ValueError` if a<0 |
| `history()` | — | list[OperationResult] | returns a copy |
| `last()` | — | OperationResult or None | last recorded operation |
| `clear()` | — | None | resets history |

---

## inventory.py

### `Product`

Dataclass representing a single product.

| Field | Type | Description |
|---|---|---|
| `sku` | str | Unique product identifier |
| `name` | str | Display name |
| `price` | float | Unit price |
| `quantity` | int | Current stock level (default 0) |

| Method | Returns | Notes |
|---|---|---|
| `is_in_stock()` | bool | True if quantity > 0 |

### `Inventory`

In-memory product store.

| Method | Parameters | Returns | Notes |
|---|---|---|---|
| `generate_report()` | — | str | Renders the inventory as an HTML report using `report.html` as the template structure. |

### report.html

New HTML template for rendering the inventory report. This file includes a table structure for displaying product details such as SKU, name, price, quantity, and status.