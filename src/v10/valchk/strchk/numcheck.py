import re
from typing import Any

from src.v10.struct.signal import ValueFormatter


def number_checker(base_temp_parse_string: str) -> tuple[int | float, int]:
    """

    :param base_temp_parse_string: str
    :return: tuple[int | float, int]
    """
    temp_parse_string = base_temp_parse_string.strip(".")

    # Int value.
    if "." not in temp_parse_string:
        match temp_parse_string[0: 2]:
            case "0b": return int(temp_parse_string[2:], 2),  ValueFormatter.BIN_NUMBER_FORMATTER  # noqa
            case "0o": return int(temp_parse_string[2:], 8),  ValueFormatter.OCT_NUMBER_FORMATTER  # noqa
            case "0d": return int(temp_parse_string[2:], 10), ValueFormatter.DEC_NUMBER_FORMATTER  # noqa
            case "0x": return int(temp_parse_string[2:], 16), ValueFormatter.HEX_NUMBER_FORMATTER  # noqa
            case _:    return int(temp_parse_string),         ValueFormatter.DEC_NUMBER_FORMATTER  # noqa

    # Float value.
    else:
        match temp_parse_string[0: 2]:
            case "0b": return float(ConversionDecimal(temp_parse_string[2:]).bin_to_dec()), ValueFormatter.BIN_NUMBER_FORMATTER  # noqa
            case "0o": return float(ConversionDecimal(temp_parse_string[2:]).oct_to_dec()), ValueFormatter.OCT_NUMBER_FORMATTER  # noqa
            case "0d": return float(temp_parse_string[2:]),                                 ValueFormatter.DEC_NUMBER_FORMATTER  # noqa
            case "0x": return float(ConversionDecimal(temp_parse_string[2:]).hex_to_dec()), ValueFormatter.HEX_NUMBER_FORMATTER  # noqa
            case _:    return float(temp_parse_string),                                     ValueFormatter.DEC_NUMBER_FORMATTER  # noqa


def parse_number_literal(value: str) -> tuple[Any, int] | None:
    """Parse a numeric literal into its real value and formatter flag."""
    if not value or not re.fullmatch(
        r"^[+-]?(?:0[bBoOxX][0-9a-fA-F_]+|0[oO][0-7_]+|0[dD]?[0-9_]+|(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9_]+)(?:[eE][+-]?[0-9_]+)?|[0-9][0-9_]*(?:[eE][+-]?[0-9_]+)?)$",
        value,
    ):
        return None

    # Replace the bottom line, this is only for watching better.
    clean_value: str = value.replace("_", "")
    sign: int = -1 if clean_value.startswith("-") else 1
    number_body: str = clean_value[1:] if clean_value[:1] in "+-" else clean_value
    lower_body: str = number_body.lower()

    # Check the number's prefix, load it with correct number system.
    try:
        if lower_body.startswith("0b"):
            return int(number_body[2:], 2) * sign, ValueFormatter.BIN_NUMBER_FORMATTER
        if lower_body.startswith("0o"):
            return int(number_body[2:], 8) * sign, ValueFormatter.OCT_NUMBER_FORMATTER
        if lower_body.startswith("0x"):
            return int(number_body[2:], 16) * sign, ValueFormatter.HEX_NUMBER_FORMATTER
        if lower_body.startswith("0d"):
            if "." in number_body or "e" in lower_body:
                return float(number_body[2:]) * sign, ValueFormatter.DEC_NUMBER_FORMATTER
            return int(number_body[2:], 10) * sign, ValueFormatter.DEC_NUMBER_FORMATTER
        if "." in number_body or "e" in lower_body:
            return float(number_body) * sign, ValueFormatter.DEC_NUMBER_FORMATTER
        return int(number_body, 10) * sign, ValueFormatter.DEC_NUMBER_FORMATTER
    except ValueError:
        return None


def int_literal_loader(token: str) -> tuple[int, int]:
    """
    Parse one integer token coming from a postfix expression.

    The BOT grammar allows the 0b / 0o / 0d / 0x bases and "_" as a thousand separator, none of
    which the built-in `int()` understands, so every literal goes through the shared scanner.

    :param token: str    The literal token, e.g. "0x1f" or "1_000".
    :return: int
    """
    parsed: tuple[int, int] | None = parse_number_literal(token)
    if parsed is None:
        raise ValueError(f"Unsupported integer literal: {token!r}")
    return int(parsed[0]), parsed[1]


def decimal_literal_loader(token: str) -> tuple[int | float, int]:
    """
    Same loader as int_literal_loader but keeps the fractional part for FLOAT expression lists.

    :param token: str    The literal token, e.g. "0.5" or "0x1f".
    :return: int | float
    """
    parsed: tuple[int | float, int] | None = parse_number_literal(token)
    if parsed is None:
        raise ValueError(f"Unsupported decimal literal: {token!r}")
    return parsed
