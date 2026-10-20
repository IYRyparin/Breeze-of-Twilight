from typing import Any
from queue import Queue

from src.v10.parser.column.calculator import *
from src.v10.parser.column.formatter import FormatChecker
from src.v10.struct.kword import ConfigurationValueReplacerKeyword
from src.v10.struct.signal import ValueFormatter
from src.v10.valchk.anychk.autochk import complex_data_type_checker
from src.v10.valchk.infix.fixchange import infix_to_postfix_with_list


class DatabasesSegmentValueChecker(object):
    def __init__(self) -> None:
        """
        This function setter is used to Check and load the value with correct type.
        It only supports the basic value. When you want
        """
        pass

    def auto_check(self, name: str) -> Any:
        """
        Return the value parser which belongs to a python type name.\n

        Every returned parser builds a *value stack* (`list[tuple[Any, formatter]]`), which is
        the representation all downstream code expects. `boolean_parser` also serves the
        IDENTIFICATION title lines where a bare bool is wanted, so it stays scalar and is simply
        wrapped here instead.

        :param name: str    Python type name, e.g. 'int', 'string', 'bool'.
        :return: Any    Callable(temp_parse_string, queue_loader[, follow]) -> value stack
        """
        match name:
            case 'int':      return self.int_number_parser     # noqa
            case 'float':    return self.float_number_parser   # noqa
            case 'bool':     return self.boolean_parser        # noqa
            case 'string':   return self.string_parser         # noqa
            case 'file':     return self.file_parser           # noqa
            case 'anything': return complex_data_type_checker  # noqa
            case 'str':      return self.string_parser         # noqa
            case _:          return None                       # noqa

    @staticmethod
    def int_number_parser(temp_parse_string: str, queue_loader: Queue[tuple[str, int]]) -> list[tuple[int | str, int]]:
        format_checker: FormatChecker = FormatChecker(temp_parse_string, queue_loader)
        format_checker.start_run()
        final_list: list[tuple[Any, int]] = format_checker.get_final_list()
        postfix_list: list[tuple[Any, int]] = infix_to_postfix_with_list(final_list)
        suffix_calc: list[tuple[int | str, int]] = complex_mathematics_suffix_int_calculator(postfix_list)
        return suffix_calc

    @staticmethod
    def float_number_parser(temp_parse_string: str, queue_loader: Queue[tuple[str, int]]) -> list[tuple[ConversionDecimal | str, int]]:
        format_checker: FormatChecker = FormatChecker(temp_parse_string, queue_loader)
        format_checker.start_run()
        final_list: list[tuple[Any, int]] = format_checker.get_final_list()
        postfix_list: list[tuple[Any, int]] = infix_to_postfix_with_list(final_list)
        suffix_calc: list[tuple[ConversionDecimal | str, int]] = complex_mathematics_suffix_decimal_calculator(postfix_list)
        return suffix_calc

    @staticmethod
    def string_parser(temp_parse_string: str, queue_loader: Queue[tuple[str, int]]) -> list[tuple[str | int, int]]:
        """
        This function is used to parse the string value, and return the correct value.\n
        :param temp_parse_string: The basic string which you want to check.
        :param queue_loader: The string saving memory, you can see it's described in parser.py.
        :return: list[tuple[str | int, int]]
        """
        format_checker: FormatChecker = FormatChecker(temp_parse_string.strip(), queue_loader)
        format_checker.start_run()
        final_list: list[tuple[Any, int]] = format_checker.get_final_list()
        postfix_list: list[tuple[Any, int]] = infix_to_postfix_with_list(final_list)
        suffix_calc: list[tuple[str | int, int]] = complex_string_suffix_calculator(postfix_list)
        return suffix_calc

    @staticmethod
    def file_parser(temp_parse_string: str, queue_loader: Queue[tuple[str, int]]) -> list[tuple[str | int, int]]:
        format_checker: FormatChecker = FormatChecker(temp_parse_string.strip(), queue_loader)
        format_checker.start_run()
        final_list: list[tuple[Any, int]] = format_checker.get_final_list()
        postfix_list: list[tuple[Any, int]] = infix_to_postfix_with_list(final_list)
        temp_suffix_calc: list[tuple[str | int, int]] = complex_string_suffix_calculator(postfix_list)
        suffix_calc: list[tuple[str | int, int]] = []
        for temp_value, temp_format in temp_suffix_calc:
            if isinstance(temp_value, str) and temp_format == ValueFormatter.DEFAULT_EMPTY_FORMATTER:
                suffix_calc.append((temp_value, ValueFormatter.FILE_STRING_FORMATTER))
        return suffix_calc

    @staticmethod
    def boolean_parser(temp_parse_string: str, _) -> list[tuple[bool, int]]:
        return [(
            temp_parse_string.lower().strip() == ConfigurationValueReplacerKeyword.TRUE,
            ValueFormatter.DEFAULT_EMPTY_FORMATTER
        )]
