import re
import functools
from ctypes import c_uint8
from queue import Queue
from typing import *

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

# ----- ASSIST FUNCTION SETTER -----
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# SETTER SEGMENT START.


@functools.lru_cache(maxsize=None)
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


@functools.lru_cache(maxsize=None)
def complex_data_type_checker(dat_info_string: str) -> tuple[Any, ctypes.c_uint8]:  # noqa
    """
    This function is used to check the complex data type, and return the correct value and format signal.\n
    The data type is following those rules.\n
    - Start with " and end with ", means it's a string.\n
    - Start with true or false, means it's a boolean.\n
    - Start with 0b, 0o, 0d, 0x, means it's a number.\n
    - Start with null, means it's a null value.\n
    - Start with [ and end with ], means it's a list.\n
    :param dat_info_string: str    The basic string which you want to check.
    :return: tuple[Any, ctypes.c_uint8]
    """
    dat_info_string: str = dat_info_string.strip()

    # 1. Check the string, both start with " and end with ".
    if dat_info_string[0] == "\"" and dat_info_string[-1] == "\"":
        if re.search(r"^\.{1,2}[\\/].*$", dat_info_string[1 : -1]) == dat_info_string[1 : -1] or re.search(r"^(?:(?:[a-zA-Z]:\\.{1,2})?[\\/](?:[^\\/?*|<>:\"]+[\\/])*)(?:(?:[^\\/?*|<>:\"]+?)(?:\.[^.\\/?*|<>:\"]+)?)?$", dat_info_string[1 : -1]) == dat_info_string[1 : -1]:  # noqa Check with correct path format.
            return str(dat_info_string[1 : -1]), ValueFormatter.FILE_STRING_FORMATTER  # noqa

        # Not a correct filepath data, return with normal.
        return str(dat_info_string[1 : -1]), ValueFormatter.DEFAULT_STRING_FORMATTER  # noqa

    # 2. Check the boolean value, just compare it is equals true or false at all.
    elif dat_info_string == "true" or dat_info_string == "false":
        return dat_info_string == "true", ValueFormatter.DEFAULT_EMPTY_FORMATTER

    # 3. Check the int value, follow the number system's rule.
    elif all([i in list("1234567890_.bodx") for i in dat_info_string]):
        temp_parse_string: str = dat_info_string.replace("_", "")

        # Check the number system.
        try:
            return number_checker(temp_parse_string)

        # If meet the error, means this may not an int value, so we can continue.
        except ValueError:
            pass

    # 4. Check list method.
    try:
        return list(dat_info_string), ValueFormatter.DEFAULT_EMPTY_FORMATTER

    # Not the correct format, continue.
    except ValueError:
        pass

    # 5. Check null method.
    if dat_info_string == "null":
        return None, ValueFormatter.DEFAULT_EMPTY_FORMATTER

    # At last, we don't understand what is it, so we can just raise the Exception.
    else:
        raise ValueError("Unsupported data type.")


def complex_mathmatics_suffix_int_calculator(dat_info_string: str) -> tuple[int, ctypes.c_uint8]:  # noqa
    """

    :param dat_info_string: str
    :return: tuple[int, ctypes.c_uint8]
    """
    calculate_stack: list[int] = []

    # Range the postfix.
    for element_item in infix_to_postfix(dat_info_string).split():
        if element_item in {"+", "-", "*", "/", "**", "//", "<<", ">>", "&", "|", "^"}:
            right_value: int = calculate_stack.pop()
            left_value:  int = calculate_stack.pop()

            # Compare and return the correct method.
            match element_item:
                case "+":  calculate_stack.append(int(left_value + right_value))
                case "-":  calculate_stack.append(int(left_value - right_value))
                case "*":  calculate_stack.append(int(left_value * right_value))
                case "/":  calculate_stack.append(int(left_value / right_value))
                case "**": calculate_stack.append(int(left_value ** right_value))
                case "//": calculate_stack.append(int(left_value // right_value))
                case "<<": calculate_stack.append(int(left_value << right_value))
                case ">>": calculate_stack.append(int(left_value >> right_value))
                case "&":  calculate_stack.append(int(left_value & right_value))
                case "|":  calculate_stack.append(int(left_value | right_value))
                case "^":  calculate_stack.append(int(left_value ^ right_value))

        # Or anything else, we can just input it into the stack.
        else:
            calculate_stack.append(int(element_item))

    # So finally, we can just return it.
    return calculate_stack[0], ValueFormatter.DEC_NUMBER_FORMATTER


@functools.lru_cache(maxsize=None)
def complex_mathmatics_suffix_decimal_calculator(dat_info_string: str) -> tuple[ConversionDecimal, ctypes.c_uint8]:  # noqa
    """
    Welp...This function is used to check and calculate the math string.
    In here, we need to change the value into the correct type and return it with the correct format signal.
    :param dat_info_string: str    The basic string which you want to check.
    :return: tuple[ConversionDecimal, ctypes.c_uint8]
    """
    calculate_stack: list[ConversionDecimal] = []

    # Range the postfix.
    for element_item in infix_to_postfix(dat_info_string).split():
        if element_item in {"+", "-", "*", "/", "**", "//", "<<", ">>", "&", "|", "^"}:
            right_value: ConversionDecimal = calculate_stack.pop()
            left_value:  ConversionDecimal = calculate_stack.pop()

            # Compare and return the correct method.
            match element_item:
                case "+":  calculate_stack.append(left_value + right_value)
                case "-":  calculate_stack.append(left_value - right_value)
                case "*":  calculate_stack.append(left_value * right_value)
                case "/":  calculate_stack.append(left_value / right_value)
                case "**": calculate_stack.append(left_value ** right_value)
                case "//": calculate_stack.append(left_value // right_value)
                case "<<": calculate_stack.append(left_value << right_value)
                case ">>": calculate_stack.append(left_value >> right_value)
                case "&":  calculate_stack.append(left_value & right_value)
                case "|":  calculate_stack.append(left_value | right_value)
                case "^":  calculate_stack.append(left_value ^ right_value)

        # Or anything else, we can just append it.
        else:
            calculate_stack.append(ConversionDecimal(element_item))

    # Finally, anything is ok, so we can return it at all.
    return calculate_stack[0], ValueFormatter.DEC_NUMBER_FORMATTER


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
    # -> From those function part, is the
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
                # TODO: In the future update, there need to input the support of the complex methods.
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
        -
        -
        -
        -
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

        # Lower the string, prepare for the parse.
        dat_info_string = dat_info_string.lower()

        # Now, just start to check the edge.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=4  # len("enum") = 4
        )

        # Push the urgent part into the new value.
        dat_info_string: str = dat_info_string[limit_range[0] : limit_range[1]]  # noqa

        # Initialize some value, and prepare for parsing.
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

                # Check and make sure that queue is in here.
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
        dat_info_string: str = dat_info_string[limit_range[0] : limit_range[1]]  # noqa

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

    # IDENTIFICATION SEGMENT PART. TO >>> SIMPLE SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def int_number_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]]) -> int:  # noqa
        temp_parse_string = temp_parse_string.lower().strip()
        temp_parse_string = temp_parse_string.replace("_", "")

        # Compare and return the correct method.
        return int(number_checker(temp_parse_string)[0])

    @staticmethod
    def float_number_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]]) -> float:  # noqa
        temp_parse_string = temp_parse_string.lower().strip()
        temp_parse_string = temp_parse_string.replace("_", "")

        # Compare and return the correct method.
        return float(number_checker(temp_parse_string)[0])

    @staticmethod
    def string_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]]) -> str:
        if queue_loader is not None:
            return queue_loader.get()

        # Start to parse the string.
        temp_parse_string = temp_parse_string.lower().strip()
        if temp_parse_string.startswith("\""): temp_parse_string = temp_parse_string[1 : ]  # noqa
        if temp_parse_string.endswith("\""):   temp_parse_string = temp_parse_string[ : -1]  # noqa
        return temp_parse_string

    @staticmethod
    def boolean_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]]) -> bool:  # noqa
        temp_parse_string = temp_parse_string.lower().strip()
        return temp_parse_string == "true"

    @staticmethod
    def null_parser(temp_parse_string: str = "", queue_loader: Optional[Queue[str]] = None, follow: type = Any) -> str:  # noqa
        match follow.__name__:
            case 'int':     return '0'          # noqa
            case 'float':   return '0.0'        # noqa
            case 'string':  return "\"\""       # noqa
            case 'list':    return '[]'         # noqa
            case 'dict':    return '{}'         # noqa
            case 'bool':    return 'False'      # noqa
            case _:         return None         # noqa


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

            # Drop out the empty part of the string.
            elif string_signal or (element_char == " " and not string_signal):
                continue

            # Check the interrupted char. That means we need to terminate input and start to check the data.
            elif element_char == "," and temp_string_memory != "":
                value_type_saver:  Any
                prefix_temp_saver: ctypes.c_uint8

                # Check the value's prefix to understand what it's mean.
                if temp_string_memory.startswith("!"):
                    prefix_temp_saver = ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE
                    temp_string_memory = temp_string_memory[1:]  # TODO: In here, need to support more formatter.
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
