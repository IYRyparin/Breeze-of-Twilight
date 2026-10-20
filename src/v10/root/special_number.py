"""Arithmetic helpers for infinity and not-a-number values."""

from __future__ import annotations

import math
from typing import TypeAlias


RealNumber: TypeAlias = int | float


def _is_number(value: object) -> bool:
    return isinstance(value, (int, float))


def _sign(value: RealNumber) -> int:
    if value == 0:
        return -1 if isinstance(value, float) and math.copysign(1.0, value) < 0 else 1
    return -1 if value < 0 else 1


def _is_odd_integer(value: RealNumber) -> bool:
    if isinstance(value, int):
        return value % 2 != 0
    return math.isfinite(value) and value.is_integer() and int(value) % 2 != 0


class NotANumber:
    """IEEE-style NaN value with arithmetic support for ``int`` and ``float``."""

    __slots__ = ()

    def __repr__(self) -> str:
        return "NotANumber()"

    def __str__(self) -> str:
        return "nan"

    def __bool__(self) -> bool:
        return True

    def __float__(self) -> float:
        return math.nan

    def __int__(self) -> int:
        raise ValueError("cannot convert NaN to integer")

    def __hash__(self) -> int:
        return object.__hash__(self)

    def __eq__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> bool:
        return True

    def __lt__(self, other: object) -> bool:
        return False

    def __le__(self, other: object) -> bool:
        return False

    def __gt__(self, other: object) -> bool:
        return False

    def __ge__(self, other: object) -> bool:
        return False

    def __neg__(self) -> NotANumber:
        return self

    def __pos__(self) -> NotANumber:
        return self

    def __abs__(self) -> NotANumber:
        return self

    def _binary(self, other: object) -> NotANumber:
        if not isinstance(other, (Infinite, NotANumber)) and not _is_number(other):
            return NotImplemented
        return self

    __add__ = __radd__ = _binary
    __sub__ = __rsub__ = _binary
    __mul__ = __rmul__ = _binary
    __truediv__ = __rtruediv__ = _binary
    __floordiv__ = __rfloordiv__ = _binary
    __mod__ = __rmod__ = _binary

    def __pow__(self, exponent: object) -> NotANumber | int:
        if _is_number(exponent) and exponent == 0:
            return 1
        if not isinstance(exponent, (Infinite, NotANumber)) and not _is_number(exponent):
            return NotImplemented
        return self

    def __rpow__(self, base: object) -> NotANumber | int:
        if _is_number(base) and base == 1:
            return 1
        if not isinstance(base, (Infinite, NotANumber)) and not _is_number(base):
            return NotImplemented
        return self


class Infinite:
    """Signed infinity supporting arithmetic with ``int`` and ``float`` values.

    Construct positive infinity with ``Infinite()`` and negative infinity with
    ``Infinite(-1)`` (or ``Infinite(sign=-1)``).
    """

    __slots__ = ("sign",)

    def __init__(self, sign: int | float = 1) -> None:
        if not _is_number(sign) or isinstance(sign, float) and math.isnan(sign) or sign == 0:
            raise ValueError("infinity sign must be a non-zero number")
        self.sign = _sign(sign)

    def __repr__(self) -> str:
        return "Infinite()" if self.sign > 0 else "Infinite(-1)"

    def __str__(self) -> str:
        return "inf" if self.sign > 0 else "-inf"

    def __bool__(self) -> bool:
        return True

    def __float__(self) -> float:
        return math.inf * self.sign

    def __int__(self) -> int:
        raise OverflowError("cannot convert infinity to integer")

    def __hash__(self) -> int:
        return hash(math.inf * self.sign)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Infinite):
            return self.sign == other.sign
        if isinstance(other, float) and math.isinf(other):
            return self.sign == _sign(other)
        return False

    def __ne__(self, other: object) -> bool:
        return not self == other

    def __lt__(self, other: object) -> bool:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return False
        if isinstance(other, Infinite):
            return self.sign < other.sign
        if _is_number(other):
            return self.sign < 0
        return NotImplemented

    def __le__(self, other: object) -> bool:
        return self == other or self < other

    def __gt__(self, other: object) -> bool:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return False
        if isinstance(other, Infinite):
            return self.sign > other.sign
        if _is_number(other):
            return self.sign > 0
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        return self == other or self > other

    def __neg__(self) -> Infinite:
        return Infinite(-self.sign)

    def __pos__(self) -> Infinite:
        return self

    def __abs__(self) -> Infinite:
        return Infinite()

    def __add__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return self if self.sign == other.sign else NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return self if self.sign == _sign(other) else NotANumber()
            return self
        return NotImplemented

    __radd__ = __add__

    def __sub__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return NotANumber() if self.sign == other.sign else self
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return NotANumber() if self.sign == _sign(other) else self
            return self
        return NotImplemented

    def __rsub__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return other - self
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return NotANumber() if _sign(other) == self.sign else Infinite(_sign(other))
            return Infinite(-self.sign)
        return NotImplemented

    def __mul__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return Infinite(self.sign * other.sign)
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return Infinite(self.sign * _sign(other))
            if other == 0:
                return NotANumber()
            return Infinite(self.sign * _sign(other))
        return NotImplemented

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return NotANumber()
            if other == 0:
                return Infinite(self.sign * _sign(other))
            return Infinite(self.sign * _sign(other))
        return NotImplemented

    def __rtruediv__(self, other: object) -> float | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return NotANumber()
            return math.copysign(0.0, _sign(other) * self.sign)
        return NotImplemented

    def __floordiv__(self, other: object) -> Infinite | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other):
                return NotANumber()
            if other == 0:
                return Infinite(self.sign * _sign(other))
            return Infinite(self.sign * _sign(other))
        return NotImplemented

    def __rfloordiv__(self, other: object) -> float | NotANumber:
        if isinstance(other, NotANumber) or isinstance(other, float) and math.isnan(other):
            return NotANumber()
        if isinstance(other, Infinite):
            return NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isinf(other) or other == 0:
                return NotANumber()
            return math.copysign(0.0, _sign(other) * self.sign)
        return NotImplemented

    def __mod__(self, other: object) -> NotANumber:
        if isinstance(other, (NotANumber, Infinite)):
            return NotANumber()
        if _is_number(other):
            return NotANumber()
        return NotImplemented

    def __rmod__(self, other: object) -> RealNumber | NotANumber:
        if isinstance(other, (NotANumber, Infinite)):
            return NotANumber()
        if _is_number(other):
            if isinstance(other, float) and math.isnan(other):
                return NotANumber()
            if isinstance(other, float) and math.isinf(other):
                return NotANumber()
            return other
        return NotImplemented

    def __pow__(self, exponent: object) -> Infinite | float | int | NotANumber:
        if isinstance(exponent, NotANumber) or isinstance(exponent, float) and math.isnan(exponent):
            return NotANumber()
        if isinstance(exponent, Infinite):
            if self.sign < 0:
                return NotANumber()
            return Infinite() if exponent.sign > 0 else 0.0
        if not _is_number(exponent):
            return NotImplemented
        if exponent == 0:
            return 1
        if exponent < 0:
            if self.sign < 0 and _is_odd_integer(exponent):
                return -0.0
            return 0.0
        return Infinite(-1 if self.sign < 0 and _is_odd_integer(exponent) else 1)

    def __rpow__(self, base: object) -> Infinite | float | int | NotANumber:
        if isinstance(base, NotANumber) or isinstance(base, float) and math.isnan(base):
            return NotANumber()
        if isinstance(base, Infinite):
            return base.__pow__(self)
        if not _is_number(base):
            return NotImplemented
        if isinstance(base, float) and math.isinf(base):
            if self.sign > 0:
                return Infinite(_sign(base))
            return math.copysign(0.0, _sign(base))
        if abs(base) == 1:
            return 1
        if base == 0:
            return 0 if self.sign > 0 else Infinite(1)
        if abs(base) > 1 and self.sign > 0:
            return Infinite(1)
        if abs(base) > 1:
            return 0.0
        if self.sign < 0:
            return Infinite(1)
        return 0.0
