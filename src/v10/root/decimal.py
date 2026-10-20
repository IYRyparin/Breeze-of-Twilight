from decimal import Decimal
from typing import Final

MAX_LENGTH: Final[int] = 100


class ConversionDecimal(object):
    _DIGITS = "0123456789ABCDEF"
    _BASE_PREFIXES = {2: "0b", 8: "0o", 16: "0x"}

    def __init__(self, number: Decimal | int | float | str) -> None:
        self._number: Decimal | int | float | str = number
        if isinstance(self._number, str):
            self._number = self._number.upper()

    def auto_changer(self) -> Decimal:
        return self._to_decimal_value()

    @classmethod
    def _parse_base(cls, value: str, base: int) -> Decimal:
        """Parse a base-2, base-8, or base-16 numeral exactly."""
        if not isinstance(value, str):
            raise TypeError("Base values must be strings.")

        text = value.strip().upper()
        prefix = cls._BASE_PREFIXES[base].upper()
        sign = 1
        if text.startswith(("+", "-")):
            if text[0] == "-":
                sign = -1
            text = text[1:]
        if text.startswith(prefix):
            text = text[len(prefix):]
        if text.count(".") > 1 or not text:
            raise ValueError(f"Invalid base-{base} number.")

        integer_part, _, fractional_part = text.partition(".")
        if not integer_part and not fractional_part:
            raise ValueError(f"Invalid base-{base} number.")
        digits = integer_part + fractional_part
        if any(char not in cls._DIGITS[:base] for char in digits):
            raise ValueError(f"Invalid base-{base} number.")

        significand = int(digits or "0", base)
        decimal_places = len(fractional_part) * (1 if base == 2 else 3 if base == 8 else 4)
        if decimal_places:
            coefficient = significand * 5**decimal_places
            decimal_digits = str(coefficient).rjust(decimal_places + 1, "0")
            result = Decimal(f"{decimal_digits[:-decimal_places]}.{decimal_digits[-decimal_places:]}")
        else:
            result = Decimal(significand)
        return result.copy_negate() if sign < 0 else result

    @classmethod
    def _format_base(cls, value: Decimal, base: int) -> str:
        """Format a Decimal in the requested base, truncating fractions at MAX_LENGTH."""
        if not value.is_finite():
            raise ValueError("Cannot convert a non-finite Decimal.")

        sign, digits, exponent = value.as_tuple()
        coefficient = int("".join(str(digit) for digit in digits) or "0")
        if exponent >= 0:
            numerator, denominator = coefficient * 10**exponent, 1
        else:
            numerator, denominator = coefficient, 10**(-exponent)

        integer_value, remainder = divmod(numerator, denominator)
        if integer_value == 0:
            integer_digits = "0"
        else:
            encoded = []
            while integer_value:
                integer_value, digit = divmod(integer_value, base)
                encoded.append(cls._DIGITS[digit])
            integer_digits = "".join(reversed(encoded))

        fractional_digits = []
        for _ in range(MAX_LENGTH):
            if remainder == 0:
                break
            remainder *= base
            digit, remainder = divmod(remainder, denominator)
            fractional_digits.append(cls._DIGITS[digit])

        prefix = cls._BASE_PREFIXES[base]
        sign_prefix = "-" if sign and coefficient else ""
        fractional_part = "".join(fractional_digits)
        return f"{sign_prefix}{prefix}{integer_digits}.{fractional_part}"

    def to_hex(self) -> str:
        return self._format_base(self._to_decimal_value(), 16)

    def hex_to_dec(self) -> Decimal:
        return self._parse_base(self._number, 16)

    def to_bin(self) -> str:
        return self._format_base(self._to_decimal_value(), 2)

    def bin_to_dec(self) -> Decimal:
        return self._parse_base(self._number, 2)

    def to_opt(self) -> str:
        return self._format_base(self._to_decimal_value(), 8)

    def oct_to_dec(self) -> Decimal:
        """
        Converts a decimal number to its operator equivalent.
        Operator numbers are base-8 numbers, which means they use the digits 0-7 to represent values. Each digit in an operator number represents a power of 8, starting from the rightmost digit (which represents 8^0) and moving left.
        The conversion process involves repeatedly dividing the decimal number by 8 and recording the remainders. The operator equivalent is then formed by reading the remainders in reverse order.
        :return: Decimal
        """
        return self._parse_base(self._number, 8)

    def _to_decimal_value(self) -> Decimal:
        """
        Internal helper to get Decimal value of the stored number.
        :return: Decimal
        """
        if isinstance(self._number, Decimal):
            return self._number

        # Accept numeric types
        if isinstance(self._number, (int, float)):
            return Decimal(str(self._number))

        if isinstance(self._number, str):
            text = self._number.strip()
            signed_text = text[1:] if text.startswith(("+", "-")) else text
            prefix = signed_text[:2].lower()
            if prefix == "0b":
                return self._parse_base(text, 2)
            if prefix == "0o":
                return self._parse_base(text, 8)
            if prefix == "0x":
                return self._parse_base(text, 16)
            return Decimal(text)

        # When otherwise, drop off the unsupported method.
        raise TypeError("Unsupported type for ConversionDecimal")

    # --- Numeric conversions and representation ---
    def __decimal__(self) -> Decimal:  # custom helper
        return self._to_decimal_value()

    def __float__(self):
        return float(self._to_decimal_value())

    def __int__(self):
        return int(self._to_decimal_value())

    def __str__(self):
        return str(self._to_decimal_value())

    def __repr__(self):
        return f"ConversionDecimal({repr(self._number)})"

    # --- Arithmetic operations returning Decimal (behave like Decimal) ---
    @staticmethod
    def _get_other_decimal(other) -> Decimal:
        if isinstance(other, ConversionDecimal):
            return other._to_decimal_value()
        return ConversionDecimal(other)._to_decimal_value()

    def __add__(self, other):
        return self._to_decimal_value() + self._get_other_decimal(other)

    def __radd__(self, other):
        return self._get_other_decimal(other) + self._to_decimal_value()

    def __sub__(self, other):
        return self._to_decimal_value() - self._get_other_decimal(other)

    def __rsub__(self, other):
        return self._get_other_decimal(other) - self._to_decimal_value()

    def __mul__(self, other):
        return self._to_decimal_value() * self._get_other_decimal(other)

    def __rmul__(self, other):
        return self._get_other_decimal(other) * self._to_decimal_value()

    def __truediv__(self, other):
        return self._to_decimal_value() / self._get_other_decimal(other)

    def __rtruediv__(self, other):
        return self._get_other_decimal(other) / self._to_decimal_value()

    def __floordiv__(self, other):
        return self._to_decimal_value() // self._get_other_decimal(other)

    def __rfloordiv__(self, other):
        return self._get_other_decimal(other) // self._to_decimal_value()

    def __mod__(self, other):
        return self._to_decimal_value() % self._get_other_decimal(other)

    def __rmod__(self, other):
        return self._get_other_decimal(other) % self._to_decimal_value()

    def __pow__(self, other, modulo=None):
        if modulo is None:
            return self._to_decimal_value() ** self._get_other_decimal(other)
        # modulo with Decimal is uncommon; attempt integer pow
        return pow(int(self._to_decimal_value()), int(self._get_other_decimal(other)), modulo)

    def __rpow__(self, other, modulo=None):
        if modulo is None:
            return self._get_other_decimal(other) ** self._to_decimal_value()
        return pow(int(self._get_other_decimal(other)), int(self._to_decimal_value()), modulo)

    # Unary ops
    def __neg__(self):
        return -self._to_decimal_value()

    def __pos__(self):
        return +self._to_decimal_value()

    def __abs__(self):
        return abs(self._to_decimal_value())

    # Comparisons
    def __eq__(self, other):
        try:
            return self._to_decimal_value() == self._get_other_decimal(other)
        except Exception:  # noqa
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self._to_decimal_value() < self._get_other_decimal(other)

    def __le__(self, other):
        return self._to_decimal_value() <= self._get_other_decimal(other)

    def __gt__(self, other):
        return self._to_decimal_value() > self._get_other_decimal(other)

    def __ge__(self, other):
        return self._to_decimal_value() >= self._get_other_decimal(other)

    # --- Bitwise and shift helpers ---
    @staticmethod
    def _bin_str_for(value) -> str:
        """Return binary string like "101.011" without 0b prefix for the given value (ConversionDecimal or plain number)."""
        if isinstance(value, ConversionDecimal):
            if value._to_decimal_value() < 0:
                raise ValueError("Bitwise operations are not defined for negative values.")
            s = value.to_bin()
        else:
            converted = ConversionDecimal(value)
            if converted._to_decimal_value() < 0:
                raise ValueError("Bitwise operations are not defined for negative values.")
            s = converted.to_bin()
        if s.startswith("0b"):
            s = s[2:]
        if "." not in s:
            s = s + "."
        return s

    @staticmethod
    def _split_bits(binstr: str) -> tuple:
        a, b = binstr.split(".")
        return a, b

    @staticmethod
    def _normalize_parts(a_int, a_frac, b_int, b_frac):
        # pad integer parts on left, fractional parts on right
        max_int = max(len(a_int), len(b_int))
        max_frac = max(len(a_frac), len(b_frac))
        a_int = a_int.rjust(max_int, '0')
        b_int = b_int.rjust(max_int, '0')
        a_frac = a_frac.ljust(max_frac, '0')
        b_frac = b_frac.ljust(max_frac, '0')
        return a_int, a_frac, b_int, b_frac

    @staticmethod
    def _strip_result(int_part: str, frac_part: str) -> tuple:
        # strip leading zeros from integer part but leave at least '0'
        int_part = int_part.lstrip('0')
        if int_part == "":
            int_part = "0"
        # strip trailing zeros from fractional part
        frac_part = frac_part.rstrip('0')
        return int_part, frac_part

    def _bitwise_binary_op(self, other, op) -> Decimal:
        """Perform bitwise op where op is function taking two bit chars returning '0' or '1'."""
        a_bin = self._bin_str_for(self)
        b_bin = self._bin_str_for(other)
        a_int, a_frac = self._split_bits(a_bin)
        b_int, b_frac = self._split_bits(b_bin)
        a_int, a_frac, b_int, b_frac = self._normalize_parts(a_int, a_frac, b_int, b_frac)
        res_int = ''.join(op(x, y) for x, y in zip(a_int, b_int))
        res_frac = ''.join(op(x, y) for x, y in zip(a_frac, b_frac))
        res_int, res_frac = self._strip_result(res_int, res_frac)
        res = res_int + ("." + res_frac if res_frac != "" else "")
        return ConversionDecimal(res).bin_to_dec()

    # Bitwise operators: and/or/xor
    def __and__(self, other):
        return self._bitwise_binary_op(other, lambda x, y: '1' if x == '1' and y == '1' else '0')

    def __or__(self, other):
        return self._bitwise_binary_op(other, lambda x, y: '1' if x == '1' or y == '1' else '0')

    def __xor__(self, other):
        return self._bitwise_binary_op(other, lambda x, y: '1' if (x != y) else '0')

    def __invert__(self):
        # unary NOT: flip bits of self representation
        a_bin = self._bin_str_for(self)
        a_int, a_frac = self._split_bits(a_bin)
        inv_int = ''.join('1' if c == '0' else '0' for c in a_int)
        inv_frac = ''.join('1' if c == '0' else '0' for c in a_frac)
        inv_int, inv_frac = self._strip_result(inv_int, inv_frac)
        res = inv_int + ("." + inv_frac if inv_frac != "" else "")
        return ConversionDecimal(res).bin_to_dec()

    # Shift operations: move the binary point
    def _shift(self, n: int) -> Decimal:
        # left shift by positive n, right by negative n
        a_bin = self._bin_str_for(self)
        int_part, frac_part = self._split_bits(a_bin)
        combined = int_part + frac_part
        cur_point = len(int_part)
        new_point = cur_point + n
        if new_point <= 0:
            # point moved left beyond leftmost bit
            zeros = '0' * (abs(new_point))
            new_combined = zeros + combined
            new_int = '0'
            new_frac = new_combined
        elif new_point >= len(combined):
            # point moved to or beyond rightmost bit
            new_combined = combined + '0' * (new_point - len(combined))
            new_int = new_combined
            new_frac = ''
        else:
            new_int = combined[:new_point]
            new_frac = combined[new_point:]
        new_int, new_frac = self._strip_result(new_int, new_frac)
        res = new_int + ("." + new_frac if new_frac != "" else "")
        return ConversionDecimal(res).bin_to_dec()

    def __lshift__(self, other):
        n = int(other)
        # left shift moves point to the right by n
        return self._shift(n)

    def __rshift__(self, other):
        n = int(other)
        # right shift moves point to the left by n
        return self._shift(-n)
