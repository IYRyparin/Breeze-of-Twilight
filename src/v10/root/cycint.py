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
