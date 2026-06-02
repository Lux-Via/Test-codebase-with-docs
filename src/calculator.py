import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class OperationResult:
    operation: str
    a: float
    b: Optional[float]
    result: float

    def __str__(self):
        if self.b is not None:
            return f"{self.a} {self.operation} {self.b} = {self.result}"
        return f"{self.operation}({self.a}) = {self.result}"


class Calculator:
    """
    Stateful calculator that keeps a history of all operations.
    """

    def __init__(self):
        self._history: list[OperationResult] = []

    def _record(self, operation: str, a: float, b: Optional[float], result: float) -> float:
        self._history.append(OperationResult(operation, a, b, result))
        return result

    def add(self, a: float, b: float) -> float:
        return self._record("+", a, b, a + b)

    def subtract(self, a: float, b: float) -> float:
        return self._record("-", a, b, a - b)

    def multiply(self, a: float, b: float) -> float:
        return self._record("*", a, b, a * b)

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return self._record("/", a, b, a / b)

    def power(self, base: float, exponent: float) -> float:
        return self._record("**", base, exponent, base ** exponent)

    def sqrt(self, a: float) -> float:
        if a < 0:
            raise ValueError("Cannot take square root of a negative number")
        return self._record("sqrt", a, None, math.sqrt(a))

    def history(self) -> list[OperationResult]:
        return list(self._history)

    def last(self) -> Optional[OperationResult]:
        return self._history[-1] if self._history else None

    def clear(self) -> None:
        self._history.clear()
