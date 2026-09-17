import math
from functools import lru_cache
from decimal import Decimal, getcontext


# ----- SOURCE START -----

# 配置默认精度（有效数字位数）
DEFAULT_PREC: int = 50
getcontext().prec = DEFAULT_PREC

# 最大允许的级数项数（防止计算过载）
MAX_TERMS = 10000


def _set_precision(prec: int):
    """设置 Decimal 全局精度"""
    if prec < 1:
        raise ValueError("精度必须 >= 1")
    getcontext().prec = prec


def _factorial_iter(n: int) -> Decimal:
    """计算 n! 并返回 Decimal 类型（n 较小，用于迭代）"""
    res = Decimal(1)
    for i in range(2, n+1):
        res *= i
    return res


def _arctan_series(x: Decimal, terms: int) -> Decimal:
    """
    计算 arctan(x) 的泰勒级数，共 terms 项
    要求 |x| <= 1，否则级数发散
    """
    if terms <= 0:
        return Decimal(0)
    result = Decimal(0)
    sign = Decimal(1)
    for n in range(terms):
        # 计算 x^(2n+1) / (2n+1)
        numerator = x ** (2*n + 1)
        denominator = Decimal(2*n + 1)
        result += sign * numerator / denominator
        sign = -sign
    return result


def _compute_pi(terms: int) -> Decimal:
    """
    使用马青公式计算 π，terms 为 arctan 级数的项数
    """
    if terms > MAX_TERMS:
        raise ValueError(f"项数 {terms} 超过最大限制 {MAX_TERMS}")
    x1 = Decimal(1) / Decimal(5)
    x2 = Decimal(1) / Decimal(239)
    pi = 16 * _arctan_series(x1, terms) - 4 * _arctan_series(x2, terms)
    return pi


def _compute_e(terms: int) -> Decimal:
    """
    计算 e = sum_{n=0}^{∞} 1/n!，共 terms 项
    """
    if terms > MAX_TERMS:
        raise ValueError(f"项数 {terms} 超过最大限制 {MAX_TERMS}")
    e = Decimal(1)          # n=0 项
    fact = Decimal(1)       # 当前 n! (n=0 时为 1)
    for n in range(1, terms):
        fact *= n           # 现在 fact = n!
        e += Decimal(1) / fact
    return e


def _reduce_angle(x: Decimal, pi: Decimal) -> Decimal:
    """
    将角度 x 规约到 [0, 2π) 区间，利用取模运算
    """
    two_pi = 2 * pi
    # Decimal 支持 % 运算
    return x % two_pi


def _compute_sin(x: Decimal, terms: int, pi: Decimal | None = None) -> Decimal:
    """
    计算 sin(x) 的泰勒级数，共 terms 项
    若提供 pi，则先规约角度加速收敛
    """
    if terms > MAX_TERMS:
        raise ValueError(f"项数 {terms} 超过最大限制 {MAX_TERMS}")
    if pi is not None:
        x = _reduce_angle(x, pi)
    # 迭代计算 sin： term_n = (-1)^n x^(2n+1)/(2n+1)!
    term = x
    result = term
    for n in range(1, terms):
        # term_n = term_{n-1} * (-1) * x^2 / ((2n)*(2n+1))
        term = -term * x * x / (Decimal(2*n) * Decimal(2*n + 1))
        result += term
    return result


def _compute_cos(x: Decimal, terms: int, pi: Decimal = None) -> Decimal:
    """
    计算 cos(x) 的泰勒级数，共 terms 项
    若提供 pi，则先规约角度加速收敛
    """
    if terms > MAX_TERMS:
        raise ValueError(f"项数 {terms} 超过最大限制 {MAX_TERMS}")
    if pi is not None:
        x = _reduce_angle(x, pi)
    # 迭代计算 cos： term_n = (-1)^n x^(2n)/(2n)!
    term = Decimal(1)
    result = term
    for n in range(1, terms):
        # term_n = term_{n-1} * (-1) * x^2 / ((2n-1)*(2n))
        term = -term * x * x / (Decimal(2*n - 1) * Decimal(2*n))
        result += term
    return result


def _compute_tan(x: Decimal, terms: int, pi: Decimal = None) -> Decimal:
    """
    计算 tan(x) = sin(x)/cos(x)
    """
    sin_val = _compute_sin(x, terms, pi)
    cos_val = _compute_cos(x, terms, pi)
    if cos_val == 0:
        raise ZeroDivisionError("tan(x) 在 cos(x)=0 处未定义")
    return sin_val / cos_val

# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# IDENTIFICATION INTERFACE. TO >>> CONFIGURATION INTERFACES.
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.

def sqrt(number: int) -> float:
    return math.sqrt(number)


def factorial(number: int) -> float:
    return math.factorial(number)


def logarithmic(number: int, base: int) -> float:
    return math.log(number, base=base)


def exponential(number: int) -> float:
    return math.exp(number)


def power(number: int, base: int) -> float:
    return math.pow(number, base)


def sin(number: float) -> float:
    return math.sin(number)


def cos(number: float) -> float:
    return math.cos(number)


def tan(number: float) -> float:
    return math.tan(number)


def asin(number: float) -> float:
    return math.asin(number)


def acos(number: float) -> float:  # noqa
    return math.acos(number)


def atan(number: float) -> float:  # noqa
    return math.atan(number)


def pi() -> float:
    return math.pi


def e() -> float:
    return math.e


@lru_cache(maxsize=None)
def high_pi(prec: int) -> Decimal:
    return _compute_pi(prec)


@lru_cache(maxsize=None)
def high_e(prec: int) -> Decimal:
    return _compute_e(prec)


@lru_cache(maxsize=None)
def high_sin(x: Decimal, terms: int, math_pi: Decimal = None) -> Decimal:
    return _compute_sin(x, terms, math_pi)


@lru_cache(maxsize=None)
def high_cos(x: Decimal, terms: int, math_pi: Decimal = None) -> Decimal:
    return _compute_cos(x, terms, math_pi)


@lru_cache(maxsize=None)
def high_tan(x: Decimal, terms: int, math_pi: Decimal = None) -> Decimal:
    return _compute_tan(x, terms, math_pi)


@lru_cache(maxsize=None)
def arctan(x, terms) -> Decimal:
    return _arctan_series(x, terms)

# CODE SEGMENT END.
# endregion
# 
# ----- SEPARATING LINE -----
# 
# IDENTIFICATION CALCULATOR. TO >>> COMPREHENSIVE CALCULATOR.
#
# region
# INTRODUCE SENTENCE.
# -> This part is used to define a comprehensive calculator function which can be used to calculate some basic mathmatics function.
# -> The comprehensive calculator function will be used in executive to calculate some basic mathmatics function.
# -> The comprehensive calculator function will be used in executive to calculate some basic mathmatics function.
#
# CODE SEGMENT START.


def comprehensive_calculator(executive: bool, *args) -> Decimal | float | int | str:
    match args[0]:
        case "sqrt":        return sqrt(args[1])                 if executive else 1  # noqa
        case "sin":         return sin(args[1])                  if executive else 1  # noqa
        case "cos":         return cos(args[1])                  if executive else 1  # noqa
        case "tan":         return tan(args[1])                  if executive else 1  # noqa
        case "asin":        return asin(args[1])                 if executive else 1  # noqa
        case "acos":        return acos(args[1])                 if executive else 1  # noqa
        case "atan":        return atan(args[1])                 if executive else 1  # noqa
        case "factorial":   return factorial(args[1])            if executive else 1  # noqa
        case "logarithmic": return logarithmic(args[1], args[2]) if executive else 2  # noqa
        case "exponential": return exponential(args[1])          if executive else 1  # noqa
        case "power":       return power(args[1], args[2])       if executive else 2  # noqa
        case "pi":          return pi()                          if executive else 0  # noqa
        case "e":           return e()                           if executive else 0  # noqa
        case "high_pi":     return high_pi(args[1])              if executive else 1  # noqa
        case "high_e":      return high_e(args[1])               if executive else 1  # noqa
        case "high_arctan": return arctan(args[1], args[2])      if executive else 2  # noqa
        case "high_sin": pass
        case "high_cos": pass
        case "high_tan": pass
        case _: raise IndexError("Invalid operator command.")

    if len(args) == 2:
        match args[0]:
            case "high_sin": return high_sin(args[1], args[2])   if executive else 23  # noqa
            case "high_cos": return high_cos(args[1], args[2])   if executive else 23  # noqa
            case "high_tan": return high_tan(args[1], args[2])   if executive else 23  # noqa
            case _: raise IndexError("Invalid operator command.")

    else:
        match args[0]:
            case "high_sin": return high_sin(args[1], args[2], args[3]) if executive else 23
            case "high_cos": return high_cos(args[1], args[2], args[3]) if executive else 23
            case "high_tan": return high_tan(args[1], args[2], args[3]) if executive else 23
            case _: raise IndexError("Invalid operator command.")


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- SOURCE END -----
