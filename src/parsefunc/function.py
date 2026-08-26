# -*- CUSTOM FUNCTION LIST -*-

import types
import typing
from decimal import Decimal
from queue import Queue


# ----- SOURCE START -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> CUSTOM VALUE.
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.

# ----- CUSTOM TYPE PART -----
# 
# region
# INTRODUCE SENTENCE.
# ->
# -> 
# -> 
# 
# CODE SEGMENT PART START.


class CyclicInt:
    """一个在指定区间内循环的整数，支持所有常规整数运算。"""

    def __init__(self, value, start, end):
        """
        :param value: 初始值（可以是任意整数）
        :param start: 区间下界（包含）
        :param end:   区间上界（不包含），必须大于 start
        """
        if end <= start:
            raise ValueError("end must be greater than start")
        self._start = start
        self._end = end
        self._range = end - start
        self._value = self._normalize(value)

    def _normalize(self, v):
        """将任意整数映射到 [start, end-1] 区间内（使用取模）"""
        return ((v - self._start) % self._range) + self._start

    # ---------- 属性访问 ----------
    @property
    def value(self):
        """获取当前循环整数的实际数值（在区间内）"""
        return self._value

    @property
    def start(self):
        return self._start

    @property
    def end(self):
        return self._end

    # ---------- 算术运算（返回新的 CyclicInt） ----------
    def __add__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        return CyclicInt(self.value + other_val, self.start, self.end)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        return CyclicInt(self.value - other_val, self.start, self.end)

    def __rsub__(self, other):
        # other - self
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        return CyclicInt(other_val - self.value, self.start, self.end)

    def __mul__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        return CyclicInt(self.value * other_val, self.start, self.end)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __floordiv__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if other_val == 0:
            raise ZeroDivisionError("division by zero")
        return CyclicInt(self.value // other_val, self.start, self.end)

    def __rfloordiv__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if self.value == 0:
            raise ZeroDivisionError("division by zero")
        return CyclicInt(other_val // self.value, self.start, self.end)

    def __mod__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if other_val == 0:
            raise ZeroDivisionError("modulo by zero")
        return CyclicInt(self.value % other_val, self.start, self.end)

    def __rmod__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if self.value == 0:
            raise ZeroDivisionError("modulo by zero")
        return CyclicInt(other_val % self.value, self.start, self.end)

    def __pow__(self, power, modulo=None):
        if isinstance(power, CyclicInt):
            power_val = power.value
        else:
            power_val = int(power)
        if power_val < 0:
            raise ValueError("negative exponent not supported")
        result = pow(self.value, power_val, modulo)
        if modulo is not None:
            # 如果提供了模数，结果已在 [0, modulo-1]，但我们需要循环到自己的区间
            # 这里简单返回 CyclicInt 归一化后的值（忽略 modulo 参数，因为不符合我们的循环语义）
            # 更好的做法：只支持两个参数，忽略 modulo
            pass
        return CyclicInt(result if modulo is None else result, self.start, self.end)

    # 一元运算
    def __neg__(self):
        return CyclicInt(-self.value, self.start, self.end)

    def __pos__(self):
        return CyclicInt(self.value, self.start, self.end)

    def __abs__(self):
        return CyclicInt(abs(self.value), self.start, self.end)

    # ---------- 就地运算（修改自身） ----------
    def __iadd__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        self._value = self._normalize(self.value + other_val)
        return self

    def __isub__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        self._value = self._normalize(self.value - other_val)
        return self

    def __imul__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        self._value = self._normalize(self.value * other_val)
        return self

    def __ifloordiv__(self, other):  # noqa
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if other_val == 0:
            raise ZeroDivisionError("division by zero")
        self._value = self._normalize(self.value // other_val)
        return self

    def __imod__(self, other):
        if isinstance(other, CyclicInt):
            other_val = other.value
        else:
            other_val = int(other)
        if other_val == 0:
            raise ZeroDivisionError("modulo by zero")
        self._value = self._normalize(self.value % other_val)
        return self

    # ---------- 比较运算 ----------
    def __eq__(self, other):
        if isinstance(other, CyclicInt):
            return self.value == other.value and self.start == other.start and self.end == other.end
        try:
            return self.value == int(other)
        except (TypeError, ValueError):
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if isinstance(other, CyclicInt):
            return self.value < other.value
        return self.value < int(other)

    def __le__(self, other):
        if isinstance(other, CyclicInt):
            return self.value <= other.value
        return self.value <= int(other)

    def __gt__(self, other):
        if isinstance(other, CyclicInt):
            return self.value > other.value
        return self.value > int(other)

    def __ge__(self, other):
        if isinstance(other, CyclicInt):
            return self.value >= other.value
        return self.value >= int(other)

    # ---------- 类型转换 ----------
    def __int__(self):
        return self.value

    def __float__(self):
        return float(self.value)

    def __bool__(self):
        return bool(self.value)

    def __index__(self):
        return self.value

    # ---------- 字符串表示 ----------
    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"CyclicInt({self.value}, {self.start}, {self.end})"

    # ---------- 哈希 ----------
    def __hash__(self):
        return hash((self.value, self.start, self.end))

    # ---------- 支持与普通 int 的混合运算（已通过 int(other) 处理） ----------
    # 但为了更安全，还可以实现 __int__ 等，已经完成


class ConversionDecimal(object):
    def __init__(self, number: Decimal | float | str) -> None:
        self._number: Decimal | float | str = number
        if isinstance(self._number, str):
            self._number = self._number.upper()

    def auto_changer(self) -> Decimal:
        if isinstance(self._number, str):
            match self._number[0 : 2]:  # noqa
                case "0b": return Decimal(self.bin_to_dec())
                case "0o": return Decimal(self.oct_to_dec())
                case "0x": return Decimal(self.hex_to_dec())
                case _:    return Decimal(self._number)  # noqa

        return Decimal(self._number)

    # ----- HEX CHANGER ------
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, is the hex changer, which is used to change the decimal number into hex number.
    # ->
    # ->
    #
    # HEX CHANGER CODE SEGMENT START.

    def to_hex(self) -> str:
        """
        Converts a decimal number to its hexadecimal equivalent.
        Hexadecimal numbers are base-16 numbers, which means they use the digits 0-9 and the letters A-F to represent values. Each digit in a hexadecimal number represents a power of 16, starting from the rightmost digit (which represents 16^0) and moving left.
        The conversion process involves repeatedly dividing the decimal number by 16 and recording the remainders. The hexadecimal equivalent is then formed by reading the remainders in reverse order.
        :return: str
        """
        temporary_integer, temporary_decimal = str(self._number).split(".")

        # Dispose the integer part of the number.
        temporary_integer: str = hex(int(temporary_integer))
        temporary_decimal_string: str = ""

        # Dispose the decimal part of the number. I don't sure that Python has this function, so in here I parse it manually.
        temporary_decimal: Decimal = Decimal(float("0." + temporary_decimal))
        decimal_queue: Queue[Decimal] = Queue()
        decimal_queue.put(temporary_decimal)

        # Start the loop to calculate the decimal.
        while not decimal_queue.empty():
            temporary_decimal: list[str] = str(decimal_queue.get() * 16).split(".")

            # On here, we can define an exit situation, when the decimal is equal to 0, we need to break the loop.
            if all([char == "0" for char in temporary_decimal[1]]):
                match temporary_decimal[0]:  # Follow the hex rules, we need to check the integer part of the number and change it into the hex number.
                    case "0":  pass  # noqa
                    case "10": temporary_decimal_string += "A"
                    case "11": temporary_decimal_string += "B"
                    case "12": temporary_decimal_string += "C"
                    case "13": temporary_decimal_string += "D"
                    case "14": temporary_decimal_string += "E"
                    case "15": temporary_decimal_string += "F"
                    case _:    temporary_decimal_string += temporary_decimal[0]

                # After that, we can break out the loop.
                break

            # After that, we will start to get the integer part of the number and check it.
            match temporary_decimal[0]:  # Follow the hex rules, we need to check the integer part of the number and change it into the hex number.
                case "10": temporary_decimal_string += "A"
                case "11": temporary_decimal_string += "B"
                case "12": temporary_decimal_string += "C"
                case "13": temporary_decimal_string += "D"
                case "14": temporary_decimal_string += "E"
                case "15": temporary_decimal_string += "F"
                case _:    temporary_decimal_string += temporary_decimal[0]

            # Put the other part into the queue.
            decimal_queue.put(Decimal("0." + temporary_decimal[1]))

        # So from here, we can return the answer.
        return temporary_integer + "." + temporary_decimal_string

    def hex_to_dec(self) -> Decimal:
        """
        Converts a hexadecimal number to its decimal equivalent.
        Hexadecimal numbers are base-16 numbers, which means they use the digits 0-9 and the letters A-F to represent values. Each digit in a hexadecimal number represents a power of 16, starting from the rightmost digit (which represents 16^0) and moving left.
        The conversion process involves multiplying each hexadecimal digit by its corresponding power of 16 and summing the results to get the decimal equivalent.
        :return: Decimal
        """
        if not isinstance(self._number, str):
            raise TypeError("Invalid hexadecimal number.")

        # After the basic checking, we can start to change the number system.
        # Before to change it, we need to initialize some value at first.
        final_decimal: Decimal = Decimal(0.0)
        countdown:     int     = len(self._number.split(".")[0]) - 1
        temp_int:      int

        # After that, we can start to change it. That's not complex, we just follow the hexadecimal's rule to do it at all.
        for decimal_char in self._number:
            if decimal_char == ".":
                continue  # Drop out the dot character.

            # Because hexadecimal is larger to normal number, so in here, we need to build some special rule.
            if ord(decimal_char) > ord('9'):
                match decimal_char:
                    case 'A': temp_int = 10
                    case 'B': temp_int = 11
                    case 'C': temp_int = 12
                    case 'D': temp_int = 13
                    case 'E': temp_int = 14
                    case 'F': temp_int = 15
                    case _: raise TypeError("Invalid hexadecimal number.")

            # Anything else, means it not in the special part, so we can parse it normally.
            else:
                temp_int = int(decimal_char)

            # Merge the value into the final decimal.
            final_decimal += Decimal(temp_int * (16 ** countdown))

        # Finally, we can return it.
        return final_decimal

    # CODE SEGMENT END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # ----- BIN CHANGER -----
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, is the bin changer, which is used to change the decimal number into bin number.
    # ->
    # ->
    #
    # BIN CHANGER CODE SEGMENT START.

    def to_bin(self) -> str:
        """
        Converts a decimal number to its binary equivalent.
        Binary numbers are base-2 numbers, which means they only use the digits 0 and 1. Each digit in a binary number represents a power of 2, starting from the rightmost digit (which represents 2^0) and moving left.
        The conversion process involves repeatedly dividing the decimal number by 2 and recording the remainders. The binary equivalent is then formed by reading the remainders in reverse order.
        :return: str
        """
        s = str(self._number)
        if "." not in s:
            s = s + ".0"
        temporary_integer, temporary_decimal = s.split(".")

        # Dispose the integer part of the number.
        temporary_integer: str = bin(int(temporary_integer))
        temporary_decimal_string: str = ""

        # Use Decimal from string to avoid float-imprecision.
        temporary_decimal: Decimal = Decimal("0." + temporary_decimal)
        decimal_queue: Queue[Decimal] = Queue()
        decimal_queue.put(temporary_decimal)

        # Start the loop to calculate the binary fractional part (multiply by 2 each step).
        while not decimal_queue.empty():
            temporary_decimal = decimal_queue.get() * 2

            # If fractional part becomes exactly 1 or 0, record and stop.
            if temporary_decimal == Decimal(1) or temporary_decimal == Decimal(0):
                temporary_decimal_string += "1" if temporary_decimal == Decimal(1) else ""
                break

            if temporary_decimal >= Decimal(1):
                temporary_decimal_string += "1"
                decimal_queue.put(temporary_decimal - 1)

            else:
                temporary_decimal_string += "0"
                decimal_queue.put(temporary_decimal)

        # All is done, so we can return those value.
        return temporary_integer + "." + temporary_decimal_string

    def bin_to_dec(self) -> Decimal:
        """
        Converts a binary number to its decimal equivalent.
        Binary numbers are base-2 numbers, which means they only use the digits 0 and 1. Each digit in a binary number represents a power of 2, starting from the rightmost digit (which represents 2^0) and moving left.
        The conversion process involves multiplying each binary digit by its corresponding power of 2 and summing the results to get the decimal equivalent.
        :return: Decimal
        """
        if not all([char in ["0", "1", "."] for char in str(self._number)]) or not isinstance(self._number, str):
            raise ValueError("Invalid binary number.")

        # After that, we can start to change the number system. That's not complex, we just can follow the rules of the binary number system. First, we can split the number into two parts, integer part and decimal part.
        final_decimal: Decimal = Decimal(0.0)
        countdown: int = len(str(self._number).split(".")[0]) - 1

        # After initializing the variables, we can start to calculate the integer part of the number. We can just follow the rules of the binary number system, and add the value into the final decimal.
        for decimal_char in str(self._number):
            if decimal_char == ".":  # Ignore the decimal point.
                continue

            # For example, we can use "2 ** 3 * 1 + 2 ** 2 * 0 + 2 ** 1 * 1 + 2 ** 0 * -1" to calculate the binary number "1101.1". So we can just follow the rules of the binary number system, and add the value into the final decimal.
            final_decimal += Decimal(int(decimal_char)) * (Decimal(2) ** countdown)
            countdown -= 1

        # Finally, we can return the final decimal number.
        return final_decimal

    # BIN CHANGER CODE SEGMENT END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> NUMBER SYSTEM CHANGER.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, is the opt changer, which is used to change the decimal number into opt number.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def to_opt(self) -> str:
        """
        Converts a decimal number to its operator equivalent.
        Operator numbers are base-8 numbers, which means they use the digits 0-7 to represent values.
        Each digit in an operator number represents a power of 8, starting from the rightmost digit (which represents 8^0) and moving left.
        The conversion process involves repeatedly dividing the decimal number by 8 and recording the remainders
        :return: str
        """
        temporary_integer, temporary_decimal = str(self._number).split(".")

        # Dispose the integer part of the number.
        temporary_integer: str = oct(int(temporary_integer))
        temporary_decimal_string: str = ""

        # Dispose the decimal part of the number. I don't sure that Python has this function, so in here I parse it manually.
        temporary_decimal: Decimal = Decimal(float("0." + temporary_decimal))
        decimal_queue: Queue[Decimal] = Queue()
        decimal_queue.put(temporary_decimal)

        # Start the loop to calculate the decimal.
        while not decimal_queue.empty():
            temporary_decimal: list[str] = str(decimal_queue.get() * 8).split(".")

            # Check out the edge situation, because octonary number system is base 8, so when the decimal is equal to 1, we need to break the loop.
            if all([char == "0" for char in temporary_decimal[1]]):
                temporary_decimal_string += temporary_decimal[0]
                break

            # When start to parse it, we can just follow the octonary number system rules, and add the integer part into the string.
            temporary_decimal_string += temporary_decimal[0]
            decimal_queue.put(Decimal("0." + temporary_decimal[1]))

        # All is done, so we can return those value.
        return temporary_integer + "." + temporary_decimal_string

    def oct_to_dec(self) -> Decimal:
        """
        Converts a decimal number to its operator equivalent.
        Operator numbers are base-8 numbers, which means they use the digits 0-7 to represent values. Each digit in an operator number represents a power of 8, starting from the rightmost digit (which represents 8^0) and moving left.
        The conversion process involves repeatedly dividing the decimal number by 8 and recording the remainders. The operator equivalent is then formed by reading the remainders in reverse order.
        :return: Decimal
        """
        if not isinstance(self._number, str):
            raise ValueError("Invalid operator number.")

        # After that, we can start to change the number system. That's not complex, we just can follow the rules of the operator number system. First, we can split the number into two parts, integer part and decimal part.
        final_decimal: Decimal = Decimal(0.0)
        countdown: int = len(self._number.split(".")[0]) - 1

        # After initializing the variables, we can start to calculate the integer part of the number. We can just follow the rules of the operator number system, and add the value into the final decimal.
        for decimal_char in str(self._number):
            if decimal_char == ".":
                continue  # Drop out the dot character.

            # For example, we can use "8 ** 3 * 1 + 8 ** 2 * 0 + 8 ** 1 * 1 + 8 ** 0 * -1" to calculate the operator number "101.1". So we can just follow the rules of the operator number system, and add the value into the final decimal.
            final_decimal += Decimal(int(decimal_char)) * (Decimal(8) ** countdown)
            countdown -= 1

        # Finally, we can return the final decimal number.
        return final_decimal

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> OPERATION IDENTIFY SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

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

        # If it's a binary/octal/hex string (contains non-decimal chars) don't attempt parse here
        if isinstance(self._number, str):
            if any(c in self._number for c in "ABCEF01".replace('1', '')):  # crude check avoid parsing non-decimal
                # fallback: try direct Decimal conversion
                try:
                    return Decimal(self._number)
                except Exception:
                    raise TypeError("Cannot convert stored value to Decimal")

            # Ensure there is a decimal point for consistency
            s = str(self._number)

            # Make sure there is a decimal point for Decimal conversion, if not present, append ".0".
            if "." not in s:
                s = s + ".0"

            # Finally, we can return the Decimal value.
            return Decimal(s)

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
        return Decimal(str(other))

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
            s = value.to_bin()
        else:
            # Ensure there is a decimal point for to_bin compatibility
            sv = str(value)
            if "." not in sv:
                sv = sv + ".0"
            s = ConversionDecimal(sv).to_bin()
        if s.startswith("0b"):
            s = s[2:]
        # Remove trailing dot if any then ensure there is a dot in representation
        if "." not in s:
            s = s + "."
        return s

    def _split_bits(self, binstr: str) -> tuple:
        a, b = binstr.split(".")
        return a, b

    def _normalize_parts(self, a_int, a_frac, b_int, b_frac):
        # pad integer parts on left, fractional parts on right
        max_int = max(len(a_int), len(b_int))
        max_frac = max(len(a_frac), len(b_frac))
        a_int = a_int.rjust(max_int, '0')
        b_int = b_int.rjust(max_int, '0')
        a_frac = a_frac.ljust(max_frac, '0')
        b_frac = b_frac.ljust(max_frac, '0')
        return a_int, a_frac, b_int, b_frac

    def _strip_result(self, int_part: str, frac_part: str) -> tuple:
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

    # CODE SEGMENT PART END.
    # endregion


class Counter(object):
    def __init__(self, value: int):
        self._value = value

    def _get_and_inc(self) -> int:
        """返回当前值，并将内部值加1"""
        v = self._value
        self._value += 1
        return v

    # ---- 转换方法 ----
    def __int__(self) -> int:
        return self._get_and_inc()

    def __float__(self) -> float:
        return float(self._get_and_inc())

    def __index__(self) -> int:
        return self._get_and_inc()

    def __str__(self) -> str:
        return str(self._get_and_inc())

    def __repr__(self) -> str:
        return repr(self._get_and_inc())

    def __bool__(self) -> bool:
        return bool(self._get_and_inc())

    # ---- 二元算术运算 ----
    def _get_other(self, other):  # noqa
        """如果 other 也是 Counter，则取其当前值并自增；否则直接返回 other"""
        if isinstance(other, Counter):
            return other._get_and_inc()
        return other

    def __add__(self, other):
        return self._get_and_inc() + self._get_other(other)

    def __radd__(self, other):
        return self._get_other(other) + self._get_and_inc()   # 右操作数时，只有 self 参与，other 不作为操作数被“调用”

    def __sub__(self, other):
        return self._get_and_inc() - self._get_other(other)

    def __rsub__(self, other):
        return self._get_other(other) - self._get_and_inc()

    def __mul__(self, other):
        return self._get_and_inc() * self._get_other(other)

    def __rmul__(self, other):
        return self._get_other(other) * self._get_and_inc()

    def __truediv__(self, other):
        return self._get_and_inc() / self._get_other(other)

    def __rtruediv__(self, other):
        return self._get_other(other) / self._get_and_inc()

    def __floordiv__(self, other):
        return self._get_and_inc() // self._get_other(other)

    def __rfloordiv__(self, other):
        return self._get_other(other) // self._get_and_inc()

    def __mod__(self, other):
        return self._get_and_inc() % self._get_other(other)

    def __rmod__(self, other):
        return self._get_other(other) % self._get_and_inc()

    def __pow__(self, other, modulo=None):
        if modulo is None:
            return pow(self._get_and_inc(), self._get_other(other))
        return pow(self._get_and_inc(), self._get_other(other), modulo)

    def __rpow__(self, other, modulo=None):
        if modulo is None:
            return pow(self._get_other(other), self._get_and_inc())
        return pow(self._get_other(other), self._get_and_inc(), modulo)

    # 位运算（略，可按相同模式添加）
    def __lshift__(self, other):
        return self._get_and_inc() << self._get_other(other)

    def __rshift__(self, other):
        return self._get_and_inc() >> self._get_other(other)

    def __and__(self, other):
        return self._get_and_inc() & self._get_other(other)

    def __xor__(self, other):
        return self._get_and_inc() ^ self._get_other(other)

    def __or__(self, other):
        return self._get_and_inc() | self._get_other(other)

    # ---- 比较运算 ----
    def __eq__(self, other):
        return self._get_and_inc() == self._get_other(other)

    def __ne__(self, other):
        return self._get_and_inc() != self._get_other(other)

    def __lt__(self, other):
        return self._get_and_inc() < self._get_other(other)

    def __le__(self, other):
        return self._get_and_inc() <= self._get_other(other)

    def __gt__(self, other):
        return self._get_and_inc() > self._get_other(other)

    def __ge__(self, other):
        return self._get_and_inc() >= self._get_other(other)

    # ---- 一元运算 ----
    def __neg__(self):
        return -self._get_and_inc()

    def __pos__(self):
        return +self._get_and_inc()

    def __abs__(self):
        return abs(self._get_and_inc())

    def __invert__(self):
        return ~self._get_and_inc()

    # ---- 增强赋值（原地操作） ----
    # 增强赋值会修改自身，应直接操作 _value 而不触发额外的自增
    def __iadd__(self, other):
        if isinstance(other, Counter):
            self._value += other._get_and_inc()   # 注意：other 会自增，但 self 不会额外自增
        else:
            self._value += other
        return self

    def __isub__(self, other):
        if isinstance(other, Counter):
            self._value -= other._get_and_inc()
        else:
            self._value -= other
        return self


# CODE SEGMENT PART END.
# endregion
# 
# ----- SEPARATING LINE -----
# 
# ----- LOOSE DICT ------
# 
# region
# INTRODUCE SENTENCE.
# -> 
# -> 
# -> 
# 
# CODE SEGMENT START.


class LooseDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(self.lower_key(key), value)

    def __getitem__(self, item):
        return super().__getitem__(self.lower_key(item))

    def __delitem__(self, key):
        super().__delitem__(self.lower_key(key))

    def update(self, another=None, **F):  # noqa
        for key, value in another.items():
            self.__setitem__(key, value)

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    @staticmethod
    def lower_key(key):
        if isinstance(key, str):
            return key.lower()
        return key


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# IDENTIFICATION FUNCTION. TO >>> TYPE CHANGER FUNCTION.
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.

# ----- TYPE CHANGER FUNCTION -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


def generic_alias_to_types(galias) -> tuple:  # noqa
    """
    Well...What can I say?
    """
    args = getattr(galias, "args", None)
    if not args:
        raise TypeError("not a parameterized generic")     # tuple[T, ...] 表示同质元素，只返回元素类型
    if len(args) == 2 and args[1] is Ellipsis:  # noqa
        return (args[0],)  # noqa
    out = []
    for a in args:  # noqa 展开 typing.Union 或 PEP604 联合类型
        union_args = getattr(a, "args", None)
        if union_args and (getattr(a, "origin", None) is typing.Union or "|" in repr(a)):
            out.extend(union_args)  # noqa
        else:
            out.append(a)
    return tuple(out)


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- ISINSTANCE LOOSE FUNCTION -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


def _normalize_type(t):
    """将 None 字面量替换为 NoneType，统一类型表示。"""
    if t is None:
        # Python 3.10+ 有 types.NoneType，这里用 type(None) 兼容旧版
        return type(None)
    return t


def type_match(t1, t2) -> bool:
    """
    判断两个类型是否“宽松相等”。

    规则：
    - 如果任意一方为 typing.Any，返回 True。
    - 如果任意一方为 typing.Union，则检查另一方是否匹配 Union 中的某个成员。
    - 提取泛型的原始类型（origin），若原始类型相同则返回 True。
    - 若两个原始类型存在子类关系（is-subclass），也返回 True。
    - 支持 types.GenericAlias 动态泛型。
    """
    t1 = _normalize_type(t1)
    t2 = _normalize_type(t2)

    # Any 短路
    if t1 is typing.Any or t2 is typing.Any:
        return True

    # 处理 Union
    origin1 = typing.get_origin(t1)
    origin2 = typing.get_origin(t2)

    # 如果一方是 Union，展开并递归检查
    if origin1 is typing.Union:
        return any(type_match(arg, t2) for arg in typing.get_args(t1))
    if origin2 is typing.Union:
        return any(type_match(t1, arg) for arg in typing.get_args(t2))

    # 提取原始类型（泛型擦除参数）
    def _get_origin(t):
        o = typing.get_origin(t)
        if o is not None:
            return o
        # 额外处理 types.GenericAlias （Python 3.9+ list[int] 等）
        if isinstance(t, types.GenericAlias):
            return t.__origin__
        return None

    o1 = _get_origin(t1)
    o2 = _get_origin(t2)

    # 如果没提取到 origin，则使用类型本身
    if o1 is None:
        o1 = t1
    if o2 is None:
        o2 = t2

    # 原始类型相等
    if o1 == o2:
        return True

    # 子类关系检查
    if isinstance(o1, type) and isinstance(o2, type):
        try:
            if issubclass(o1, o2) or issubclass(o2, o1):  # noqa
                return True
        except TypeError:
            pass

    return False


def isinstance_loose(obj, type_hint) -> bool:
    """类似于 isinstance，但使用宽松的类型兼容规则，同时支持两种类型的直接比较。"""
    return type_match(type(obj) if not isinstance(obj, type) else obj, type_hint)


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- REPR TYPE CHANGE -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


"""
类型提示与纯数据结构表示的互相转换。

支持的类型与表示规则（Python 3.10+）：
    - Any            →  typing.Any（单例本身）
    - 普通类型 T      →  类对象 T（如 int, str）
    - list[X]        →  [X]                      （单元素列表）
    - tuple[X,Y,...] →  (X, Y, ...)              （元组）
    - dict[K, V]     →  {K: V}                   （单键值对字典）
    - Union[X,Y,...] →  [X, Y, ...]              （长度 ≥2 的列表）
    - Optional[X]    →  等价于 Union[X, None]，
        转换时统一用 [X, NoneType] 表示，还原时若检测到 [X, NoneType] 则返回 Optional[X]。

限制与约定：
    - 不支持 set/frozenset 类型，因其元素可能不可哈希，无法用简单数据结构表示。
    - Union 使用长度 ≥2 的列表表示，因此单元素 Union（无实际意义）会与 list[X] 冲突，不予支持。
    - 所有表示结构均为纯 Python 数据类型，不含自定义类。
    - 空元组类型 tuple[()] 表示为 ()，可变长同构元组 tuple[X, ...] 表示为 (X, Ellipsis)。
"""


def type_to_repr(tp):
    """
    将类型提示转换为普通数据结构表示。

    参数:
        tp: 类型表达式，如 list[int]、tuple[str, int]、int | None 等。

    返回:
        对应的纯数据结构表示。例如：
        - tuple[str, int, list[str], typing.Any] → (str, int, [str], typing.Any)
        - dict[str, list[int]]                   → {str: [int]}
        - int | None                             → [int, <class 'NoneType'>]
        - Optional[float]                        → [float, <class 'NoneType'>]
    """
    # 1. Any 是单例，直接返回
    if tp is typing.Any:
        return typing.Any

    origin = typing.get_origin(tp)

    # 2. 普通类型（如 int, str, NoneType 等），没有 __origin__
    if origin is None:
        return tp

    args = typing.get_args(tp)

    # 3. 处理各种泛型
    # list / List
    if origin in (list, typing.List):
        return [type_to_repr(args[0])]

    # tuple / Tuple
    if origin in (tuple, typing.Tuple):
        return tuple(type_to_repr(a) for a in args)

    # dict / Dict
    if origin in (dict, typing.Dict):
        if len(args) != 2:
            raise ValueError("Dict type must have exactly two arguments")
        return {type_to_repr(args[0]): type_to_repr(args[1])}  # noqa

    # Union（包括 X | Y 和 typing.Union）
    if origin in (typing.Union, types.UnionType):
        # 使用列表表示，长度等于参数个数
        return [type_to_repr(a) for a in args]

    # 其他未支持的泛型（如 set, frozenset）
    raise TypeError(f"Unsupported generic type: {tp!r}")


def repr_to_type(obj):
    """
    将普通数据结构表示还原为类型提示。

    参数:
        obj: 符合约定的数据结构，如 (str, int, [str], typing.Any)、
             {str: [int]}、[int, NoneType] 等。

    返回:
        对应的类型提示。例如：
        - (str, int, [str], typing.Any)          → tuple[str, int, list[str], typing.Any]
        - {str: [int]}                           → dict[str, list[int]]
        - [int, <class 'NoneType'>]              → Optional[int]
        - [int, str]                             → int | str
        - ()                                     → tuple[()]
    """
    # 1. Any 单例
    if obj is typing.Any:
        return typing.Any

    # 2. 普通类型（class 对象）
    if isinstance(obj, type):
        return obj

    # 3. 列表表示：可能是 list[X] 或 Union[X, Y, ...]
    if isinstance(obj, list):
        if len(obj) == 1:
            # 单元素列表 -> list[X]
            return list[repr_to_type(obj[0])]  # noqa

        # 多元素列表 -> Union / Optional
        items = [repr_to_type(e) for e in obj]
        none_type = type(None)  # <class 'NoneType'>

        # 如果恰好两个元素且其中一个是 NoneType，则还原为 Optional
        if len(items) == 2 and none_type in items:
            other = items[0] if items[1] is none_type else items[1]
            return typing.Optional[other]  # noqa

        # 否则构建 Union（使用 | 运算符合并）
        result = items[0]  # noqa
        for t in items[1:]:
            result = result | t
        return result

    # 4. 元组表示 -> tuple[...]
    if isinstance(obj, tuple):
        # 支持空元组 tuple[()] 和可变长同构元组 tuple[X, ...]
        return tuple[tuple(repr_to_type(e) for e in obj)]  # noqa

    # 5. 字典表示 -> dict[K, V]
    if isinstance(obj, dict):
        if len(obj) != 1:
            raise ValueError(
                "Dict type representation must have exactly one key-value pair"
            )
        k, v = next(iter(obj.items()))
        return dict[repr_to_type(k), repr_to_type(v)]  # noqa

    # 6. 其他类型暂不支持
    raise TypeError(f"Unsupported representation: {obj!r}")


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# -----ALGORITHM LOADER -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


def infix_to_postfix(infix: str) -> str:
    """

    :param infix: str
    :return: str
    """
    priority_dictionary: dict[int, list[str]] = {
        5: ["(", ")"],
        4: ["**"],
        3: ["*", "/", "//"],
        2: ["+", "-"],
        1: ["|", "^", "&", "<<", ">>"]
    }

    # Add shift operators into priority dictionary (do not hard-code priorities elsewhere)
    # Place shifts at level 1 (same as other bitwise ops) unless user customizes dict later.
    # Ensure they are present without duplicating.
    for lvl, ops in list(priority_dictionary.items()):
        if isinstance(ops, (list, tuple, set)):
            if '<<' not in ops:
                priority_dictionary[lvl] = list(ops)
    # we append shifts into level 1
    if 1 in priority_dictionary:
        if '<<' not in priority_dictionary[1]:
            priority_dictionary[1].append('<<')
        if '>>' not in priority_dictionary[1]:
            priority_dictionary[1].append('>>')
    else:
        priority_dictionary[1] = ['<<', '>>']

    # Normalize priority_dictionary into operator -> priority mapping (op_priority).
    op_priority: dict[str, int] = {}
    # Detection: if keys are ints (priority->ops), convert; otherwise assume op->priority mapping
    try:
        if any(isinstance(k, int) for k in priority_dictionary.keys()):
            for level, ops in priority_dictionary.items():
                try:
                    lvl = int(level)
                except Exception:
                    continue
                if isinstance(ops, (list, tuple, set)):
                    for op in ops:
                        if isinstance(op, str):
                            op_priority[op] = lvl
                elif isinstance(ops, str):
                    op_priority[ops] = lvl
        else:
            # operator -> priority mapping
            for k, v in priority_dictionary.items():
                try:
                    op_priority[str(k)] = int(v)
                except Exception:
                    continue
    except Exception:
        op_priority = {}

    # Initializing...
    signal_element_stack: list[str] = []
    number_element_stack: list[str] = []

    # Start to change the string.
    i = 0
    n = len(infix)
    # If True, next token should be a number (handles unary +/ -)
    expecting_number = True

    def _parse_number(s: int) -> tuple[str, int]:
        """Parse a number starting at index s. Returns (token, new_index).
        Supports optional base prefixes (0b,0o,0d,0x), underscores and decimal point.
        """
        if s >= n:
            return "", s
        j = s
        tok = ""
        # base-prefixed number
        if j + 1 < n and infix[j] == '0' and infix[j + 1].lower() in 'boxd':
            tok += infix[j:j+2].lower()
            base_char = infix[j+1].lower()
            j += 2
            if base_char == 'b':
                valid = set('01')
            elif base_char == 'o':
                valid = set('01234567')
            elif base_char == 'd':
                valid = set('0123456789')
            else:  # x
                valid = set('0123456789abcdefABCDEF')
            while j < n and (infix[j] in valid or infix[j] == '_' or infix[j] == '.'):
                tok += infix[j]
                j += 1
            return tok, j
        # plain decimal-like number (may contain underscores and a single dot)
        has_dot = False
        while j < n:
            ch = infix[j]
            if ch == '_':
                tok += ch
                j += 1
                continue
            if ch == '.':
                if has_dot:
                    break
                has_dot = True
                tok += ch
                j += 1
                continue
            if ch.isdigit():
                tok += ch
                j += 1
                continue
            break
        return tok, j

    while i < n:
        ch = infix[i]
        if ch.isspace():
            i += 1
            continue

        # Parentheses
        if ch == '(':
            signal_element_stack.append(ch)
            i += 1
            expecting_number = True
            continue
        if ch == ')':
            # pop until matching '('
            while signal_element_stack and signal_element_stack[-1] != '(':
                number_element_stack.append(signal_element_stack.pop())
            if signal_element_stack and signal_element_stack[-1] == '(':
                signal_element_stack.pop()
            i += 1
            expecting_number = False
            continue

        # Number (including handling unary + and -)
        if expecting_number and (ch.isdigit() or ch == '.' or (ch in '+-' and i + 1 < n and (infix[i+1].isdigit() or infix[i+1] == '.' or (infix[i+1] == '0' and i+2 < n and infix[i+2].lower() in 'boxd')))):
            sign = ''
            if ch in '+-':
                sign = ch
                i += 1
                if i >= n:
                    break
            token, new_i = _parse_number(i)
            if token == "":
                # fallback: treat sign as operator
                i = new_i
            else:
                # normalize: remove underscores, normalize prefix to lower-case
                token_norm = token.replace('_', '')
                # keep sign if present
                if sign:
                    token_norm = sign + token_norm
                number_element_stack.append(token_norm)
                i = new_i
                expecting_number = False
                continue

        # Operators (handle multi-char '**', '<<', '>>')
        op = None
        # check for multi-char operators first
        if ch == '*' and i + 1 < n and infix[i + 1] == '*':
            op = '**'
            i += 2
        elif ch == '<' and i + 1 < n and infix[i + 1] == '<':
            op = '<<'
            i += 2
        elif ch == '>' and i + 1 < n and infix[i + 1] == '>':
            op = '>>'
            i += 2
        elif ch == '/' and i + 1 < n and infix[i + 1] == '/':
            op = '//'
            i += 2
        else:
            op = ch
            i += 1

        # If operator is recognized, apply shunting-yard rules
        if op in op_priority:
            # determine associativity: '**' is right-associative
            while signal_element_stack and signal_element_stack[-1] != '(' and signal_element_stack[-1] in op_priority:
                top = signal_element_stack[-1]
                p1 = op_priority.get(op, 0)
                p2 = op_priority.get(top, 0)
                if op == '**':
                    # right-assoc: pop while p1 < p2
                    should_pop = p1 < p2
                else:
                    # left-assoc: pop while p1 <= p2
                    should_pop = p1 <= p2
                if should_pop:
                    number_element_stack.append(signal_element_stack.pop())
                else:
                    break
            signal_element_stack.append(op)
            expecting_number = True
            continue

        # Unknown character: treat as single-char token (put into output)
        number_element_stack.append(op)
        expecting_number = True

    # Pop remaining operators
    while signal_element_stack:
        top = signal_element_stack.pop()
        if top in ('(', ')'):
            # mismatched parentheses - ignore
            continue
        number_element_stack.append(top)

    # So finally, we can return it.
    final_saving_string = " ".join(number_element_stack)

    # So finally, we can return it.
    return final_saving_string


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT END.
# endregion
