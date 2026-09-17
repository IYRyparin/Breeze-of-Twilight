import ast
import re
from ctypes import c_uint8, c_ubyte
from queue import Queue
from typing import *

from src.parsefunc.function import infix_to_postfix_string
from src.parseutil.kword import ConfigurationStatusExecutiveKeyword, CALCULATE_CHAR
from src.parsefunc.exception import *
from src.parsefunc.function import LooseDict, infix_to_postfix, ConversionDecimal
from src.parseutil.kword import LEGAL_STRING_WORD, ConfigurationExtensionKeyword, STATUS_CHAR
from src.parseutil.signal import ValueFormatter, ExtensionExplainFormatter, TypeExplainFormatter


# ----- SOURCE START -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> PARSER COLUMN.
#
# region
# INTRODUCE SENTENCE.
# -> Well...As you all know, this is a data type's standalone parse setter. Work with the parser's main file.
# -> It runs with the database's check, used to merge the type checker to give some convenient method to parse the config file.
# -> Why I do that? Well...if I don't, the main parser file will be too large!
#
# CODE SEGMENT START.

# ----- ASSIST CHECKER FUNCTION SETTER -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# SETTER SEGMENT START.


def calculate_dispose(first: Any, second: Any, event: str) -> Any:
    match event:
        case "+":  return first + second    # noqa
        case "-":  return first - second    # noqa
        case "*":  return first * second    # noqa
        case "/":  return first / second    # noqa
        case "**": return first ** second   # noqa
        case "//": return first // second   # noqa
        case "<<": return first << second   # noqa
        case ">>": return first >> second   # noqa
        case "&":  return first & second    # noqa
        case "|":  return first | second    # noqa
        case "^":  return first ^ second    # noqa
        case _:    raise TypeError(event)   # noqa


def number_checker(base_temp_parse_string: str) -> tuple[int | float, ctypes.c_uint8]:
    """

    :param base_temp_parse_string: str
    :return: tuple[int | float, ctypes.c_uint8]
    """
    temp_parse_string = base_temp_parse_string.strip(".")

    # Int value.
    if "." not in temp_parse_string:
        match temp_parse_string[0: 2]:  # noqa
            case "0b": return int(temp_parse_string[2:], 2),  ValueFormatter.BIN_NUMBER_FORMATTER  # noqa
            case "0o": return int(temp_parse_string[2:], 8),  ValueFormatter.OCT_NUMBER_FORMATTER  # noqa
            case "0d": return int(temp_parse_string[2:], 10), ValueFormatter.DEC_NUMBER_FORMATTER  # noqa
            case "0x": return int(temp_parse_string[2:], 16), ValueFormatter.HEX_NUMBER_FORMATTER  # noqa
            case _:    return int(temp_parse_string),         ValueFormatter.DEC_NUMBER_FORMATTER  # noqa

    # Float value.
    else:
        match temp_parse_string[0: 2]:  # noqa
            case "0b": return float(ConversionDecimal(temp_parse_string[2:]).bin_to_dec()), ValueFormatter.BIN_NUMBER_FORMATTER  # noqa
            case "0o": return float(ConversionDecimal(temp_parse_string[2:]).oct_to_dec()), ValueFormatter.OCT_NUMBER_FORMATTER  # noqa
            case "0d": return float(temp_parse_string[2:]),                                 ValueFormatter.DEC_NUMBER_FORMATTER  # noqa
            case "0x": return float(ConversionDecimal(temp_parse_string[2:]).hex_to_dec()), ValueFormatter.HEX_NUMBER_FORMATTER  # noqa
            case _:    return float(temp_parse_string),                                     ValueFormatter.DEC_NUMBER_FORMATTER  # noqa


def brackets_edge_index_checker(dat_info_string: str,
                                right_move:      int,
                                left_bracket:    str  = "<",
                                right_bracket:   str  = ">",
                                string_ignore:   bool = True) -> tuple[int, int]:
    """

    :param string_ignore:
    :param left_bracket:
    :param right_bracket:
    :param dat_info_string: str    The basic string which you want to check.
    :param right_move: int   Right move's counter, escape useless part.
    :return: tuple[int, int]
    """
    first_final_message: int  = 0  # noqa
    last_final_message:  int  = 0
    string_signal:       bool = False

    # Start the loop and check for the left limit signal, typically start with '<'.
    if dat_info_string[right_move] != left_bracket:
        for index, dat_char in enumerate(dat_info_string[right_move : ]):  # noqa
            if (index >= 1 and dat_char == "\"" and dat_info_string[right_move + index - 1] != "\\") or (index == 0 and dat_char == "\""):
                string_signal = not string_signal

            # Search the left bracket. When we need to ignore the string, we need to check the signal in here.
            if string_ignore:
                if dat_char == left_bracket and not string_signal:  # Find the left bracket, so we can just break the loop.
                    break

            # Or anything else, we can just ignore the signal.
            else:
                if dat_char == left_bracket:
                    break

        # When we found the limit of the right range, means there is no any start limit in here.
        else:
            raise IndexError("Error part of the string.")

        # Load the first final message into the value.
        first_final_message: int = index

    # Or anything else, we can just load the start place into the value.
    else:
        first_final_message: int = right_move

    # Change the basic string, make it shorter to convenient next loop.
    dat_info_string = dat_info_string[first_final_message + 1 : ]  # noqa

    # After that, start to check the right angle bracket's index.
    if dat_info_string[-1] != right_bracket:
        for index, dat_char in enumerate(dat_info_string[ : : -1]):  # noqa
            if (index >= 1 and dat_char == "\"" and dat_info_string[right_move + index - 1] != "\\") or (index == 0 and dat_char == "\""):
                string_signal = not string_signal

            # When we need to ignore the string, we need to check the signal.
            if string_ignore:
                if dat_char == right_bracket and not string_signal:
                    break

            # Or anything else, just ignore it.
            else:
                if dat_char == right_bracket:
                    break

        # When we found the limit of the left range, means there is no any end limit in here.
        else:
            raise IndexError("Error part of the string.")

    # Or anything else, we can just load the end place into the value.
    else:
        last_final_message: int = len(dat_info_string) - 1

    # Finally, we can return them.
    return first_final_message, last_final_message


def first_signal_edge_checker(origin_string: str, signal_start: str, signal_end: str) -> int:
    """

    :param signal_end: str
    :param signal_start: str
    :param origin_string: str
    :return: int
    """
    string_signal: bool = False
    deep_signal:   int  = 0

    # Start the loop.
    for origin_index, origin_char in enumerate(origin_string):
        if origin_char == "\"" and (origin_index == 0 or origin_string[origin_index - 1] != "\\"):
            string_signal = not string_signal

        # Check and increase the deep.
        elif origin_char == signal_start and not string_signal:
            deep_signal += 1

        # Check and decrease the signal.
        elif origin_char == signal_end and not string_signal:
            deep_signal -= 1

            # Check is zero or not.
            if deep_signal == 0:
                return origin_index

    # Or anything else, just raise the Exception.
    raise IndexError("Cannot find the correct edge of the signal.")


def _is_file_string_literal(value: str) -> bool:
    """Return whether the quoted value is a file path-like string."""
    if not value:
        return False

    file_pattern = r"^(?:\.{1,2}[\\/].*|(?:[a-zA-Z]:\\.{1,2})?[\\/](?:[^\\/?*|<>:\"]+[\\/])*(?:[^\\/?*|<>:\"]+?(?:\.[^.\\/?*|<>:\"]+)?)?)$"
    return bool(re.fullmatch(r"^\.{1,2}[\\/].*$", value)) or bool(re.fullmatch(file_pattern, value))


def _parse_number_literal(value: str) -> tuple[Any, ctypes.c_uint8] | None:
    """Parse a numeric literal into its real value and formatter flag."""
    if not value or not re.fullmatch(
        r"^[+-]?(?:0[bBoOxX][0-9a-fA-F_]+|0[oO][0-7_]+|0[dD]?[0-9_]+|(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9_]+)(?:[eE][+-]?[0-9_]+)?|[0-9][0-9_]*(?:[eE][+-]?[0-9_]+)?)$",
        value,
    ):
        return None

    clean_value = value.replace("_", "")
    sign = -1 if clean_value.startswith("-") else 1
    number_body = clean_value[1:] if clean_value[:1] in "+-" else clean_value
    lower_body = number_body.lower()

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


def complex_data_type_checker(dat_info_string: str) -> tuple[Any, ctypes.c_uint8]:
    """Return the parsed value and format signal for a configuration literal."""
    dat_info_string = dat_info_string.strip()
    if not dat_info_string:
        raise ValueError("Unsupported data type.")

    # Quoted strings.
    if len(dat_info_string) >= 2 and dat_info_string[0] == '"' and dat_info_string[-1] == '"':
        target_string = dat_info_string[1:-1]
        if _is_file_string_literal(target_string):
            return str(target_string), ValueFormatter.FILE_STRING_FORMATTER
        return str(target_string), ValueFormatter.DEFAULT_STRING_FORMATTER

    lowered = dat_info_string.lower()

    # Boolean and null keywords.
    if lowered == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_TRUE:
        return True, ValueFormatter.DEFAULT_EMPTY_FORMATTER
    if lowered == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_FALSE:
        return False, ValueFormatter.DEFAULT_EMPTY_FORMATTER
    if lowered == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_NULL:
        return None, ValueFormatter.DEFAULT_EMPTY_FORMATTER

    # Numeric literals.
    numeric_value = _parse_number_literal(dat_info_string)
    if numeric_value is not None:
        return numeric_value

    # Container literals.
    if (
        (dat_info_string.startswith("[") and dat_info_string.endswith("]"))
        or (dat_info_string.startswith("{") and dat_info_string.endswith("}"))
        or (dat_info_string.startswith("(") and dat_info_string.endswith(")"))
    ):
        try:
            return ast.literal_eval(dat_info_string), ValueFormatter.DEFAULT_EMPTY_FORMATTER
        except (SyntaxError, ValueError):
            pass

    raise ValueError("Unsupported data type.")


# SETTER SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- ASSIST CALCULATOR FUNCTION SETTER -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# SETTER SEGMENT START.


def _value_format_change(dat_info_string: tuple[str, list[int]]) -> list[tuple[str, c_uint8]]:
    """
    This function is used to change the value explain data's format.

    :param dat_info_string: tuple[str, list[int]]
    :return: list[tuple[str, c_uint8]]
    """
    final_return_list: list[tuple[str, c_uint8]] = []
    value_counter:     int                       = 0
    iter_counter:      int                       = 0
    string_signal:     bool                      = False

    # Start the range and check the value in here.
    for element_index, element_item in enumerate(dat_info_string[0].split()):
        load_signal: c_uint8 = ValueFormatter.DEFAULT_EMPTY_FORMATTER

        # Check the format signal, change it when we find that it is the formatter value.
        if element_item not in CALCULATE_CHAR or string_signal:
            value_counter += 1
            if len(dat_info_string[1]) > 0 and value_counter == dat_info_string[1][iter_counter]:
                load_signal = ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER
                iter_counter += 1

        # Load the value into the final list.
        final_return_list.append((element_item, load_signal))

    # Finally, we can just return it.
    return final_return_list


def complex_mathmatics_suffix_int_calculator(dat_info_string: tuple[str, list[int]], signal_check: bool = True) -> list[tuple[int | str, c_ubyte]]:
    """

    :param signal_check: bool
    :param dat_info_string: tuple[str, list[int]]
    :return: tuple[int, ctypes.c_uint8]
    """
    calculate_stack:      list[tuple[int | str, c_uint8]] = []
    origin_data:          list[tuple[str, c_uint8]]       = _value_format_change(dat_info_string)

    # Range the postfix.
    for element_item in origin_data:
        if element_item[0] in {"+", "-", "*", "/", "**", "//", "<<", ">>", "&", "|", "^"}:
            right_value: tuple[int | str, c_uint8] = calculate_stack.pop()
            left_value:  tuple[int | str, c_uint8] = calculate_stack.pop()

            # Compare and return the correct method.
            if (right_value[1] == ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER or left_value[1] == ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER) and signal_check:
                calculate_stack.append(left_value)
                calculate_stack.append(right_value)
                calculate_stack.append(element_item)
            else:
                calculate_stack.append((calculate_dispose(left_value[0], right_value[0], element_item[0]), ValueFormatter.DEFAULT_EMPTY_FORMATTER))

        # Or anything else, we can just input it into the stack.
        else:
            calculate_stack.append((int(element_item[0]), element_item[1]))

    # So finally, we can just return it.
    return calculate_stack


def complex_mathmatics_suffix_decimal_calculator(dat_info_string: tuple[str, list[int]], signal_check: bool = True) -> list[tuple[ConversionDecimal | str, c_ubyte]]:
    """
    Welp...This function is used to check and calculate the math string.
    In here, we need to change the value into the correct type and return it with the correct format signal.
    :param dat_info_string: str    The basic string which you want to check.
    :param signal_check: bool    Whether to check the value explain signal or not.
    :return: tuple[ConversionDecimal, ctypes.c_uint8]
    """
    calculate_stack:      list[tuple[ConversionDecimal | str, c_uint8]] = []
    origin_data:          list[tuple[str, c_uint8]]                     = _value_format_change(dat_info_string)

    # Range the postfix.
    for element_item in origin_data:
        if element_item[0] in CALCULATE_CHAR:
            right_value: tuple[ConversionDecimal | str, c_uint8] = calculate_stack.pop()
            left_value:  tuple[ConversionDecimal | str, c_uint8] = calculate_stack.pop()

            # Compare and return the correct method.
            if (right_value[1] == ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER or left_value[1] == ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER) and signal_check:
                calculate_stack.append(left_value)
                calculate_stack.append(right_value)
                calculate_stack.append(element_item)
            else:
                calculate_stack.append((calculate_dispose(left_value[0], right_value[0], element_item[0]), left_value[1]))

        # Or anything else, we can just append it.
        else:
            calculate_stack.append((ConversionDecimal(element_item[0]), element_item[1]))

    # Finally, anything is ok, so we can return it at all.
    return calculate_stack


def complex_string_suffix_calculator(string_load_list: list[str | int], postfix_inject_index_list: list[int]) -> list[tuple[str | int, c_uint8]]:
    """

    :param string_load_list: list[str | int]
    :param postfix_inject_index_list: list[int]
    :return: list[tuple[str | int, c_uint8]]
    """
    temp_load_stack:        list[tuple[str | int, c_uint8]] = []
    explain_search_pointer: int                             = 0
    value_search_pointer:   int                             = 0

    # When nothing happens, we can just load it as normal.
    if len(postfix_inject_index_list) == 0 and len(string_load_list) == 1:
        return [(string_load_list[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

    # Start the loop to merge the string in here.
    else:
        for saving_item in string_load_list:
            push_index: int = postfix_inject_index_list[explain_search_pointer]
            explain_signal: c_uint8 = ValueFormatter.DEFAULT_EMPTY_FORMATTER

            # Check the index of the value is the formatter or not.
            if saving_item not in {"+", "*"}:
                if value_search_pointer == push_index:
                    explain_search_pointer += 1
                    explain_signal = ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER

                # Merge the value into stack.
                temp_load_stack.append((saving_item, explain_signal))
                value_search_pointer += 1

            # Or anything else, we can start to merge it when all is not the mutable formatter.
            else:
                value_search_pointer += 1
                first_string: tuple[str | int, c_uint8] = temp_load_stack.pop()
                second_string: tuple[str | int, c_uint8] = temp_load_stack.pop()

                # Check the format, and calculate the string.
                if first_string[1] == ValueFormatter.DEFAULT_EMPTY_FORMATTER and second_string[1] == ValueFormatter.DEFAULT_EMPTY_FORMATTER:
                    if saving_item == "+" and isinstance(second_string[0], str) and isinstance(first_string[0], str):
                        temp_load_stack.append((first_string[0] + second_string[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER))  # noqa
                    elif saving_item == "*" and isinstance(second_string[0], int) and isinstance(first_string[0], str):
                        temp_load_stack.append((first_string[0] * second_string[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER))  # noqa
                    else:
                        raise ValueError(f"Error formatter: {first_string[0]} and {second_string[0]}")

                # Or else, just return it as normal, follow LIFO, like nothing happen.
                else:
                    temp_load_stack.append(second_string)
                    temp_load_stack.append(first_string)

    # Finally, return the stack here.
    return temp_load_stack


def format_checker(value: str) -> tuple[str, list[int]]:
    """
    This function is used to check the format signal in the string.\n
    Format signal in Breeze of Twilight is "FORMAT" keyword and "FORMAT DEFAULT XXX" sentence.\n
    It seems like the format string, but for safety and easy to see, so I use this keyword except sentence like '%s、%d'.
    :param value: str
    :return: tuple[str, list[int]]
    """
    temp_saving_string:  str       = ""
    final_return_list:   list[int] = []
    string_signal:       bool      = False
    sentence_index:      int       = 0
    sentence_char:       str

    # Start the loop and try to check the signal in here.
    while sentence_index < len(value):
        drop:          bool = True
        sentence_char: str  = value[sentence_index]

        # Check we are in the string or not.
        if sentence_char == "\"" and (sentence_index == 0 or value[sentence_index - 1] != "\\"):
            string_signal = not string_signal
            drop = False

        # Merge the char into the value.
        if not string_signal and sentence_char in LEGAL_STRING_WORD[:-12]:
            temp_saving_string += sentence_char
            drop = False

        # Search the blank signal, check the keyword.
        if (sentence_char == " " or sentence_index == len(value) - 1) and not string_signal and temp_saving_string.strip() == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_FORMAT:
            next_search_index:  int = sentence_index + 1
            format_start_index: int = sentence_index - 6
            next_search_string: str
            while next_search_index < len(value) and value[next_search_index] == " ":
                next_search_index += 1

            # Start the next part of the search, try to find the default value in here.
            try:
                next_search_string: str = value[next_search_index:next_search_index + 7]
                if next_search_string != ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_DEFAULT:
                    raise IndexError

            # Cause the error, means that it don't have any default value, we can append the 'NULL'.
            except IndexError:
                tmp = list(value)
                tmp.insert(next_search_index, ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_DEFAULT + " NULL")
                value = "".join(tmp)

            next_search_index += 8  # There must be at least one space between keyword 'default' and the default value.

            # Drop out the useless space in here.
            while next_search_index < len(value) and value[next_search_index] == " ":
                next_search_index += 1

            # Initialize some memory to save the default value.
            temp_load_default_value_index: int = next_search_index
            next_search_string = ""
            next_search_char: str = value[next_search_index]

            # Search and repair the default value.
            while (string_signal or next_search_char in LEGAL_STRING_WORD[:-1] + ".()") and next_search_index < len(value):
                if next_search_char == "\"" and value[next_search_index - 1] != "\\":
                    string_signal = not string_signal
                next_search_string += next_search_char  # Search and add the default value in here.
                next_search_index += 1

            # so in here, we can get the default string value.
            default_value: Any = value[temp_load_default_value_index:next_search_index + 1]
            tmp: list[str] = list(value)
            del tmp[format_start_index:next_search_index]
            tmp.insert(format_start_index + 1, default_value)
            value = "".join(tmp)
            final_return_list.append(format_start_index)

        # Or anything else, we can just clear the memory.
        if drop:
            temp_saving_string = ""

        # Finally, increase the index and just continue in here.
        sentence_index += 1
        continue

    # Change the value's count into the number's count.
    repair_list: list[int] = []
    if len(final_return_list) > 0:
        value_counter: int = 0
        string_signal = False
        final_return_iter = iter(final_return_list)
        location_index: int = next(final_return_iter)

        # Start the loop, check and change the index.
        for index, char in enumerate(value):
            if char == "\"" and (index == 0 or value[index - 1] != "\\"):
                string_signal = not string_signal
            elif char in CALCULATE_CHAR or index == len(value) - 1:
                value_counter += 1

            # Check the count in here.
            if index == location_index:
                repair_list.append(value_counter)
                try:
                    location_index = next(final_return_iter)
                except StopIteration:
                    pass

    # So finally, we can just return them.
    return value, repair_list


# SETTER SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- PARSER FUNCTION SETTER -----
#
# region
# INTRODUCE SENTENCE.
# -> Ok, from here, is the function setter, which used to check the segment type and return the correct value.
# ->
# ->
#
# SETTER SEGMENT START.


class DatabasesSegmentTypeChecker(object):
    def __init__(self) -> None:
        """
        :return: None
        """
        pass

    def dict_checker(self, string: str) -> Any:
        CHECKING_DICTIONARY: LooseDict = LooseDict({  # noqa
            # +---------------+--------------------------------------+
            # |      KEY      |                VALUE                 |
            # +---------------+--------------------------------------+
            "int":              self.int_segment_type_checker,
            "string":           self.string_segment_type_checker,
            "float":            self.float_segment_type_checker,
            "bool":             self.bool_segment_type_checker,
            "database":         self.databases_segment_type_checker,
            "file":             self.file_segment_type_checker,
            "anything":         self.anything_segment_type_checker,
            "enum":             self.enum_segment_type_checker,
            "table":            self.table_segment_type_checker
            # +---------------+--------------------------------------+
        })
        key = string.strip().lower()

        # Common shorthand aliases mapping
        aliases = {
            'str': 'string',
            'dbl': 'float',
            'flt': 'float'
        }
        if key in aliases:
            key = aliases[key]

        # Return the correct value (function pointer).
        return CHECKING_DICTIONARY[key]

    # IDENTIFICATION SETTER SEGMENT PART. TO >>> NORMAL SEGMENT TYPE CHECKER PART.
    # 
    # region
    # INTRODUCE SENTENCE.
    # -> 
    # -> 
    # -> 
    # 
    # SETTER SEGMENT PART START.

    @staticmethod
    def int_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [int], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def float_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [float], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def string_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [str], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def bool_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [bool], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def databases_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [dict], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def file_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [str], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def anything_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        return [Any], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    # SETTER SEGMENT PART END.
    # endregion
    # 
    # ----- SEPARATING LINE -----
    # 
    # IDENTIFICATION SETTER SEGMENT PART. TO >>> COMPLEX SEGMENT TYPE CHECKER PART.
    # 
    # region
    # INTRODUCE SENTENCE.
    # -> From those function part, is the complex type checker, which used to check the complex type and return the correct value.
    # ->
    # ->
    # 
    # SETTER SEGMENT PART START.

    def table_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], c_uint8]:  # noqa
        """
        Welp...This part of function is used to parse the table type.
        It will return a type value and a format signal, which means the value's type and value's format.
        So from here, it can realize data's type information and make it easy to check it.
        :param dat_info_string: str     The basic string which you want to check.
        :return: tuple[type, ctypes.c_uint8]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")

        # Lower the string, prepare for the parse.
        dat_info_string: str = dat_info_string.lower()

        # After that, we can mark the index to prepare for next part. From here, we will start to check the edge of the table.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=5
        )

        # Get the edge, push it into the limit range and get the string which has been filed.
        table_element_type_info_string: str = dat_info_string[limit_range[0] : limit_range[1]]  # noqa

        # Delete the useless value.
        del limit_range

        # Load a list to save the type.
        final_saving_list: list[type] = []
        limit_countdown:   int        = 0
        string_signal:     bool       = False  # This is prepared for the future.

        # Start to the next loop, check the value and save it to the list.
        for element_index, element_char in enumerate(table_element_type_info_string):
            tempo_string_value: str = ''

            # In some place, we can use this signal to ignore some useless condition.
            if not string_signal:
                if element_char in list(LEGAL_STRING_WORD):  # noqa Load the string into the temp string space.
                    tempo_string_value += element_char
                    continue

                # Check the pause signal ',' and prepare for input the final type.
                elif element_char == "," and limit_countdown == 0:
                    final_element_type: type = self.dict_checker(tempo_string_value)
                    final_saving_list.append(final_element_type)
                    tempo_string_value = ''  # noqa Clean the temp value and prepare for next loop.

                    # After that, we are nothing to do, so we can just jump into next loop and don't need to wait for it.
                    del final_element_type
                    continue

                # Drop out some useless char in here.
                elif element_char == " " and not string_signal:
                    continue

                # Mark down the string, drop out the part.
                elif element_index >= 1 and element_char == "\"" and table_element_type_info_string[element_index - 1] != "\\":
                    string_signal = not string_signal

                # Mark down the special value, make sure we can load it all into the string.
                elif element_char == "<": limit_countdown += 1  # noqa
                elif element_char == ">": limit_countdown -= 1  # noqa

        # So after all is done, we can just return it. Well...don't forget to change it.
        return final_saving_list, TypeExplainFormatter.LIST_TYPE_EXPLAIN

    def union_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type], ctypes.c_uint8]:  # noqa
        """
        This function will return a type value and a format signal, which means the value's type and value's format.\n
        From the UNION type, is following those rules.\n
        - Start with UNION keyword, use <> to block the detail information.\n
        - Each element in the union is separated by a comma.\n
        - The type of each element is checked individually.\n
        - Result is a list of types, and the format signal is a default type explain.\n
        - Final value's type need to be included in the list.\n
        :param dat_info_string: str     The basic string which you want to check.
        :return: tuple[type, ctypes.c_uint8]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")

        # Lower the string, prepare for the parse.
        dat_info_string = dat_info_string.lower()

        # Now, we can start the UNION type's parsing right now.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=5
        )

        # Push the urgent part into new value.
        dat_info_string: str = dat_info_string[limit_range[0] : limit_range[1]]  # noqa

        # Initialize some value.
        final_saving_list:  list[type] = []
        temp_saving_string: str = ''
        string_signal:      bool = False

        # Start the loop to check the value.
        for element_index, element_char in enumerate(dat_info_string):
            if element_char in list(LEGAL_STRING_WORD):  # noqa
                temp_saving_string += element_char
                continue

            # Check the edge signal.
            elif element_char == "," and not string_signal:
                final_element_type: type = self.dict_checker(temp_saving_string)
                final_saving_list.append(final_element_type)
                temp_saving_string = ''
                continue

            # Ignore useless char.
            elif element_char == " " and not string_signal:
                continue

            # Mark down the string, drop out the part.
            elif element_index >= 1 and element_char == "\"" and dat_info_string[element_index - 1] != "\\":
                string_signal = not string_signal

        # Finally, return them.
        return final_saving_list, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def enum_segment_type_checker(dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[tuple[Any, ctypes.c_uint8]], ctypes.c_uint8]:  # noqa
        """
        This function is used to check the Enum data's type and value's format.\n
        The Enum data type is following those rules.\n
        - Start with ENUM keyword, use <> to block the detail information.\n
        - Default type is ANYTHING, ENUM is similar to: -> Limit().\n
        - Support all the data's type except DATABASE.
        :param dat_info_string: str     The basic string which you want to check.
        :return: tuple[list[Any], ctypes.c_uint8]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")

        # Lower the string and check the edge in here.
        dat_info_string = dat_info_string.lower()
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=4  # len("enum") = 4
        )

        # Push the urgent part into the new value.
        dat_info_string:    str                              = dat_info_string[limit_range[0] : limit_range[1]]  # noqa
        final_saving_list:  list[tuple[Any, ctypes.c_uint8]] = []
        temp_saving_string: str                              = ''
        string_signal:      bool                             = False

        # Start to parse the data.
        for element_index, element_char in enumerate(dat_info_string):
            if element_char in list(LEGAL_STRING_WORD):  # noqa
                temp_saving_string += element_char

            # Check out the terminate signal.
            elif element_char == "," and not string_signal:
                value_loader: tuple[Any, c_uint8] = complex_data_type_checker(temp_saving_string)
                if isinstance(value_loader[0], str) and queue_loader is not None:
                    value_loader = (queue_loader.get(), value_loader[1])

                # Append the value into the list and clear the temp string.
                final_saving_list.append(value_loader)
                temp_saving_string = ''

            # Drop out the useless value in here.
            elif element_char == " " and not string_signal:
                continue

            # Check the string signal.
            elif element_index >= 1 and element_char == "\"" and dat_info_string[element_index - 1] != "\\":
                string_signal = not string_signal

        # At last, so we can return them.
        return final_saving_list, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    def conversion_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[type, ctypes.c_uint8]:  # noqa
        """

        :param dat_info_string: str     The basic string which you want to convert.
        :return: tuple[type, ctypes.c_uint8]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")

        # Lower the string, prepare for the parse.
        dat_info_string = dat_info_string.lower()

        # Start to check the limit range.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=10  # len("conversion") = 10
        )

        # Push the urgent part.
        dat_info_string: str = dat_info_string[limit_range[0]:limit_range[1]]

        # And...Because this only has one segment, so we can just return it.
        del limit_range
        return self.dict_checker(dat_info_string), ValueFormatter.CUSTOM_CONVERSION_FORMATTER

    # SETTER SEGMENT PART END.
    # endregion
    # 
    # ----- SEPARATING LINE -----


class DatabasesSegmentValueChecker(object):
    def __init__(self, value_type: Optional[list[type]], explain: Optional[ctypes.c_uint8]) -> None:
        """

        :param value_type: list[type]
        :param explain: ctypes.c_uint8
        """
        self._value_type: list[type]     = value_type if value_type is not None else []
        self._explain:    ctypes.c_uint8 = explain if explain is not None else ctypes.c_uint8(0x00)

    def auto_check(self, name: str) -> Any:
        match name:
            case 'int':   return self.int_number_parser     # noqa
            case 'float': return self.float_number_parser   # noqa
            case 'bool':  return self.boolean_parser        # noqa
            case 'str':   return self.string_parser         # noqa
            case 'null':  return self.null_parser           # noqa
            case _:       return None                       # noqa

    @staticmethod
    def int_number_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]], follow: type = Any) -> list[tuple[int | str, c_ubyte]]:  # noqa
        calculate_string_loader: tuple[str, list[int]] = format_checker(temp_parse_string)
        calculate_string_loader = infix_to_postfix(calculate_string_loader[0]), calculate_string_loader[1]
        return complex_mathmatics_suffix_int_calculator(calculate_string_loader)

    @staticmethod
    def float_number_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]], follow: type = Any) -> list[tuple[ConversionDecimal | str, c_ubyte]]:  # noqa
        calculate_string_loader: tuple[str, list[int]] = format_checker(temp_parse_string)
        calculate_string_loader = infix_to_postfix(calculate_string_loader[0]), calculate_string_loader[1]
        return complex_mathmatics_suffix_decimal_calculator(calculate_string_loader)

    @staticmethod
    def string_parser(temp_parse_string: str, queue_loader: Queue[str], follow: type = Any) -> list[tuple[str | int, c_ubyte]]:  # noqa
        """
        This function is used to parse the string value, and return the correct value.\n
        :param temp_parse_string: str    The basic string which you want to check.
        :param queue_loader: Queue[str]   The string saving memory, you can see it's described in parser.py.
        :return: list[tuple[str | int, c_ubyte]]
        """
        temp_parse_string = temp_parse_string.strip()   # Clean he blank signal.
        string_signal:       bool = False               # A boolean value, express that we are in the string or not.
        final_saving_string: str  = ""                  # Used to save the final string of the first part.

        # Start the first part of the loop.
        # Start to check the string, if it starts with a double quote, we can just return it directly.
        for element_index, element_char in enumerate(temp_parse_string):
            if element_char == "\"" and (element_index == 0 or temp_parse_string[element_index - 1] != "\\"):
                string_signal = not string_signal
                if not string_signal:
                    final_saving_string += f"\"{queue_loader.get()}\""

            # Search the operation char.
            elif element_char in {"+", "*", "(", ")"} and not string_signal:
                final_saving_string += element_char

        # All is over, so we can start next part of the parsing, just merge and return the stack here.
        final_saving_string, postfix_inject_index_list = format_checker(final_saving_string)
        return complex_string_suffix_calculator(infix_to_postfix_string(final_saving_string), postfix_inject_index_list)

    @staticmethod
    def boolean_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]], follow: type = Any) -> bool:  # noqa
        return temp_parse_string.lower().strip() == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_TRUE

    @staticmethod
    def null_parser(temp_parse_string: str = "", queue_loader: Optional[Queue[str]] = None, follow: type = Any) -> str:  # noqa
        match follow.__name__:
            # +-----------+----------------------+
            # |   TYPE    |     DEFAULT VALUE    |
            # +-----------+----------------------+
            case 'int':     return '0'          # noqa
            case 'float':   return '0.0'        # noqa
            case 'string':  return "\"\""       # noqa
            case 'list':    return '[]'         # noqa
            case 'dict':    return '{}'         # noqa
            case 'bool':    return 'False'      # noqa
            case _:         return None         # noqa
            # +-----------+----------------------+


class DatabaseSegmentExtensionRequireChecker(object):
    def __init__(self,
                 value_type: list[type] | None = None,
                 explain: ctypes.c_uint8 | None = None) -> None:
        """

        :param value_type: list[type] | None
        :param explain: ctypes.c_uint8 | None
        """
        self._value_parser_heap: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker(
            value_type=value_type,
            explain=explain
        )

    def auto_return(self, dat_info_string: str) -> Any:
        """

        :param dat_info_string: str
        :return: Any
        """
        dat_info_string = dat_info_string.lower().strip()

        # Find the edge, defines at '(' and ')'.
        bracket: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=0,
            left_bracket="(",
            right_bracket=")",
        )

        # Get the bracket's index, load the information signal.
        explain_signal: str = dat_info_string[ : bracket[0]]  # noqa
        del bracket

        # Match and return the signal.
        match explain_signal:
            case ConfigurationExtensionKeyword.EXECUTIVE_KEYWORD_LIMIT:   return self.limit_rule_explain            # noqa
            case ConfigurationExtensionKeyword.EXECUTIVE_KEYWORD_REGULAR: return self.regular_rule_explain
            case _:                                                       raise TypeError("Unknown explain type.")  # noqa

    def limit_rule_explain(self,
                           dat_info_string: str,
                           value_type: type,
                           string_saving_memory: Queue[str]) -> list[tuple[Any, ctypes.c_uint8]]:
        """

        :param dat_info_string: type    The basic string which you want to check.
        :param value_type: list[str]    Limited value's type.
        :param string_saving_memory: Queue[str]   The string saving memory, you can see it's described in parser.py.
        :return: list[tuple[Any, ctypes.c_uint8]]
        """
        dat_info_string:    str                              = dat_info_string.lower().strip()
        temp_string_memory: str                              = ""
        final_saving_list:  list[tuple[Any, ctypes.c_uint8]] = []
        string_signal:      bool                             = False

        # Add the end signal into the end of the string to parse normally.
        if not dat_info_string.endswith(","):
            dat_info_string = dat_info_string + ","

        # Start the loop to check the data.
        for element_index, element_char in enumerate(dat_info_string):
            if element_char in list(LEGAL_STRING_WORD + STATUS_CHAR) and not string_signal:  # Load the legal char into the element.
                temp_string_memory += element_char

            # Check the string.
            elif element_index >= 1 and element_char == "\"" and dat_info_string[element_index - 1] != "\\":
                string_signal = not string_signal

                # Change the value into the correct part of it.
                if not string_signal:
                    temp_string_memory = string_saving_memory.get()

                # Drop out other part, because we don't need it.
                continue

            # Check the interrupted char. That means we need to terminate input and start to check the data.
            elif element_char == "," and temp_string_memory != "":
                value_type_saver:  Any
                prefix_temp_saver: ctypes.c_uint8

                # Check the value's prefix to understand what it's mean.
                if temp_string_memory.startswith(ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_EXCLUDE):
                    prefix_temp_saver = ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE
                    temp_string_memory = temp_string_memory[7:]
                else:
                    prefix_temp_saver = ExtensionExplainFormatter.LIMIT_WITHIN_VALUE

                # Match and get the correct type of the value.
                match value_type.__name__:  # Owing to the undeniably profound fact, so in this version, it can't parse complex data like list, database, and so on.
                    case "int":   value_type_saver = self._value_parser_heap.int_number_parser(temp_string_memory, None)
                    case "float": value_type_saver = self._value_parser_heap.float_number_parser(temp_string_memory, None)
                    case "str":   value_type_saver = string_saving_memory.get()
                    case "bool":  value_type_saver = self._value_parser_heap.boolean_parser(temp_string_memory, None)
                    case "file":  value_type_saver = string_saving_memory.get()
                    case _:       value_type_saver = complex_data_type_checker(temp_string_memory)[0]

                # Append the final information into the list.
                final_saving_list.append((value_type_saver, prefix_temp_saver))
                temp_string_memory = ""  # Clean the buffer.

        # So finally, we can return it.
        return final_saving_list

    @staticmethod
    def regular_rule_explain(dat_info_string: str, string_saving_memory: Queue[str]) -> list[tuple[str, ctypes.c_uint8]]:
        """

        :param string_saving_memory:
        :param dat_info_string: str
        :return: list[tuple[Any, ctypes.c_uint8]]
        """
        dat_info_string:   str                              = dat_info_string.strip()
        final_saving_list: list[tuple[Any, ctypes.c_uint8]] = []
        string_signal:     bool                             = False
        string_loader:     str                              = ""

        # Load regular string from queue. In here, data string just used to check the prefix and count of the string.
        for element_index, element_char in enumerate(dat_info_string):
            if element_char == "\"" and (element_index == 0 or dat_info_string[element_index - 1] != "\\"):
                string_signal = not string_signal

            # Check the quit signal, load string into the list.
            if (element_char == "," or element_index >= len(dat_info_string) - 1) and not string_signal:
                prefix_index:   int     = 0
                regular_signal: c_uint8 = ExtensionExplainFormatter.LIMIT_WITHIN_STRING_REGULAR

                # Search and append the prefix index in here.
                while string_loader[prefix_index] != "\"":
                    match string_loader[prefix_index]:
                        case '!': regular_signal = ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR
                        case _:   pass  # noqa

                # Check and push the value into here.
                final_saving_list.append((string_saving_memory.get(), regular_signal))  # noqa
                string_loader = ""

            # Add other char into the loader.
            string_loader += element_char

        # Finally, return the list.
        return final_saving_list


# SETTER SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SOURCE END -----
