import ast
import re
from ctypes import c_uint8, c_ubyte
from queue import Empty, Queue
from typing import *

from src.parsefunc.exception import *
from src.parsefunc.function import LooseDict, infix_to_postfix, ConversionDecimal
from src.parsefunc.function import infix_to_postfix_string
from src.parseutil import kword as keyword
from src.parseutil.kword import ConfigurationStatusExecutiveKeyword, CALCULATE_CHAR
from src.parseutil.kword import LEGAL_STRING_WORD, ConfigurationExtensionKeyword
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


ESCAPE_SEQUENCE_DICT: dict[str, str] = {
    "\\\\": "\\", "\\\"": "\"", "\\'": "'",
    "\\r": "\r", "\\n": "\n", "\\a": "\a", "\\b": "\b", "\\f": "\f", "\\t": "\t", "\\v": "\v",
    "\\x00": "\x00", "\\x01": "\x01", "\\x02": "\x02", "\\x03": "\x03", "\\x04": "\x04", "\\x05": "\x05",
    "\\x06": "\x06", "\\x07": "\x07", "\\x08": "\x08", "\\x09": "\x09", "\\x0A": "\x0A", "\\x0B": "\x0B",
    "\\x0C": "\x0C", "\\x0D": "\x0D", "\\x0E": "\x0E", "\\x0F": "\x0F", "\\x10": "\x10", "\\x11": "\x11",
    "\\x12": "\x12", "\\x13": "\x13", "\\x14": "\x14", "\\x15": "\x15", "\\x16": "\x16", "\\x17": "\x17",
    "\\x18": "\x18", "\\x19": "\x19", "\\x1A": "\x1A", "\\x1B": "\x1B", "\\x1C": "\x1C", "\\x1D": "\x1D",
    "\\x1E": "\x1E", "\\x1F": "\x1F", "\\x20": "\x20", "\\x21": "\x21", "\\x22": "\x22", "\\x23": "\x23",
    "\\x24": "\x24", "\\x25": "\x25", "\\x26": "\x26", "\\x27": "\x27", "\\x28": "\x28", "\\x29": "\x29",
    "\\x2A": "\x2A", "\\x2B": "\x2B", "\\x2C": "\x2C", "\\x2D": "\x2D", "\\x2E": "\x2E", "\\x2F": "\x2F",
    "\\x30": "\x30", "\\x31": "\x31", "\\x32": "\x32", "\\x33": "\x33", "\\x34": "\x34", "\\x35": "\x35",
    "\\x36": "\x36", "\\x37": "\x37", "\\x38": "\x38", "\\x39": "\x39", "\\x3A": "\x3A", "\\x3B": "\x3B",
    "\\x3C": "\x3C", "\\x3D": "\x3D", "\\x3E": "\x3E", "\\x3F": "\x3F", "\\x40": "\x40", "\\x41": "\x41",
    "\\x42": "\x42", "\\x43": "\x43", "\\x44": "\x44", "\\x45": "\x45", "\\x46": "\x46", "\\x47": "\x47",
    "\\x48": "\x48", "\\x49": "\x49", "\\x4A": "\x4A", "\\x4B": "\x4B", "\\x4C": "\x4C", "\\x4D": "\x4D",
    "\\x4E": "\x4E", "\\x4F": "\x4F", "\\x50": "\x50", "\\x51": "\x51", "\\x52": "\x52", "\\x53": "\x53",
    "\\x54": "\x54", "\\x55": "\x55", "\\x56": "\x56", "\\x57": "\x57", "\\x58": "\x58", "\\x59": "\x59",
    "\\x5A": "\x5A", "\\x5B": "\x5B", "\\x5C": "\x5C", "\\x5D": "\x5D", "\\x5E": "\x5E", "\\x5F": "\x5F",
    "\\x60": "\x60", "\\x61": "\x61", "\\x62": "\x62", "\\x63": "\x63", "\\x64": "\x64", "\\x65": "\x65",
    "\\x66": "\x66", "\\x67": "\x67", "\\x68": "\x68", "\\x69": "\x69", "\\x6A": "\x6A", "\\x6B": "\x6B",
    "\\x6C": "\x6C", "\\x6D": "\x6D", "\\x6E": "\x6E", "\\x6F": "\x6F", "\\x70": "\x70", "\\x71": "\x71",
    "\\x72": "\x72", "\\x73": "\x73", "\\x74": "\x74", "\\x75": "\x75", "\\x76": "\x76", "\\x77": "\x77",
    "\\x78": "\x78", "\\x79": "\x79", "\\x7A": "\x7A", "\\x7B": "\x7B", "\\x7C": "\x7C", "\\x7D": "\x7D",
    "\\x7E": "\x7E", "\\x7F": "\x7F", "\\x80": "\x80", "\\x81": "\x81", "\\x82": "\x82", "\\x83": "\x83",
    "\\x84": "\x84", "\\x85": "\x85", "\\x86": "\x86", "\\x87": "\x87", "\\x88": "\x88", "\\x89": "\x89",
    "\\x8A": "\x8A", "\\x8B": "\x8B", "\\x8C": "\x8C", "\\x8D": "\x8D", "\\x8E": "\x8E", "\\x8F": "\x8F",
    "\\x90": "\x90", "\\x91": "\x91", "\\x92": "\x92", "\\x93": "\x93", "\\x94": "\x94", "\\x95": "\x95",
    "\\x96": "\x96", "\\x97": "\x97", "\\x98": "\x98", "\\x99": "\x99", "\\x9A": "\x9A", "\\x9B": "\x9B",
    "\\x9C": "\x9C", "\\x9D": "\x9D", "\\x9E": "\x9E", "\\x9F": "\x9F", "\\xA0": "\xA0", "\\xA1": "\xA1",
    "\\xA2": "\xA2", "\\xA3": "\xA3", "\\xA4": "\xA4", "\\xA5": "\xA5", "\\xA6": "\xA6", "\\xA7": "\xA7",
    "\\xA8": "\xA8", "\\xA9": "\xA9", "\\xAA": "\xAA", "\\xAB": "\xAB", "\\xAC": "\xAC", "\\xAD": "\xAD",
    "\\xAE": "\xAE", "\\xAF": "\xAF", "\\xB0": "\xB0", "\\xB1": "\xB1", "\\xB2": "\xB2", "\\xB3": "\xB3",
    "\\xB4": "\xB4", "\\xB5": "\xB5", "\\xB6": "\xB6", "\\xB7": "\xB7", "\\xB8": "\xB8", "\\xB9": "\xB9",
    "\\xBA": "\xBA", "\\xBB": "\xBB", "\\xBC": "\xBC", "\\xBD": "\xBD", "\\xBE": "\xBE", "\\xBF": "\xBF",
    "\\xC0": "\xC0", "\\xC1": "\xC1", "\\xC2": "\xC2", "\\xC3": "\xC3", "\\xC4": "\xC4", "\\xC5": "\xC5",
    "\\xC6": "\xC6", "\\xC7": "\xC7", "\\xC8": "\xC8", "\\xC9": "\xC9", "\\xCA": "\xCA", "\\xCB": "\xCB",
    "\\xCC": "\xCC", "\\xCD": "\xCD", "\\xCE": "\xCE", "\\xCF": "\xCF", "\\xD0": "\xD0", "\\xD1": "\xD1",
    "\\xD2": "\xD2", "\\xD3": "\xD3", "\\xD4": "\xD4", "\\xD5": "\xD5", "\\xD6": "\xD6", "\\xD7": "\xD7",
    "\\xD8": "\xD8", "\\xD9": "\xD9", "\\xDA": "\xDA", "\\xDB": "\xDB", "\\xDC": "\xDC", "\\xDD": "\xDD",
    "\\xDE": "\xDE", "\\xDF": "\xDF", "\\xE0": "\xE0", "\\xE1": "\xE1", "\\xE2": "\xE2", "\\xE3": "\xE3",
    "\\xE4": "\xE4", "\\xE5": "\xE5", "\\xE6": "\xE6", "\\xE7": "\xE7", "\\xE8": "\xE8", "\\xE9": "\xE9",
    "\\xEA": "\xEA", "\\xEB": "\xEB", "\\xEC": "\xEC", "\\xED": "\xED", "\\xEE": "\xEE", "\\xEF": "\xEF",
    "\\xF0": "\xF0", "\\xF1": "\xF1", "\\xF2": "\xF2", "\\xF3": "\xF3", "\\xF4": "\xF4", "\\xF5": "\xF5",
    "\\xF6": "\xF6", "\\xF7": "\xF7", "\\xF8": "\xF8", "\\xF9": "\xF9", "\\xFA": "\xFA", "\\xFB": "\xFB",
    "\\xFC": "\xFC", "\\xFD": "\xFD", "\\xFE": "\xFE", "\\xFF": "\xFF",
    "\uFFFF": "\"", "\uFFFE": ";",  # noqa
}


def is_escaped_char(base_string: str, index: int) -> bool:
    """
    Whether the character at `index` is escaped, i.e. protected by an odd run of backslashes.

    A cheap "previous char is a backslash" test is wrong: in `\\\\\\\\"` the quote is NOT escaped,
    and the comment stripper, the literal extractor and every bracket matcher have to agree.

    :param base_string: str    Whole string being scanned.
    :param index: int          Position of the candidate character.
    :return: bool
    """
    backslash_run: int = 0
    scan_index:    int = index - 1

    while scan_index >= 0 and base_string[scan_index] == "\\":
        backslash_run += 1
        scan_index -= 1

    return backslash_run % 2 == 1


def unescape_string(base_string: str) -> str:
    """
    Decode every escape sequence of one raw literal in a single left-to-right pass.

    Chained str.replace calls were used before, which re-decode the produced text: `a\\\\b`
    became `a\\b` while passing through the `\\\\ -> \\` rule, and then the `\\" -> "` rule
    attacked the freshly produced backslash, so a literal backslash in front of a quote got eaten.

    :param base_string: str    Raw literal content.
    :return: str
    """
    final_string: str = ""
    index:        int = 0

    # Start the loop to parse the string value in here.
    while index < len(base_string):
        char: str = base_string[index]
        if char == "\\" and index + 1 < len(base_string):
            sequence: str = base_string[index:index + 2]
            final_string += ESCAPE_SEQUENCE_DICT.get(sequence, sequence)
            index += 2
            continue

        # The two transient markers use single character codes, see `ReplacerDatabase`.
        if char in ("\uFFFF", "\uFFFE"):    # noqa
            final_string += ESCAPE_SEQUENCE_DICT[char]
            index += 1
            continue

        # Add the char into the buffer.
        final_string += char
        index += 1

    # So finally, we can just return the final string.
    return final_string


def take_saved_string(string_saving_memory: Optional[Queue[str]], context: str = "string literal") -> str:
    """
    Pull one pre-decoded string out of the saving memory.

    Every `"..."` literal inside a BOT file is extracted up-front into this queue and is meant
    to be consumed exactly once, in source order. Using the blocking `Queue.get()` here means
    ANY misalignment (a doubled read, a synthesized literal, an unterminated quote) makes the
    parser hang forever with no diagnostics at all, so reads are always non-blocking and an
    exhausted queue is reported as a syntax problem instead.

    :param string_saving_memory: Queue[str]   The string saving memory, see parser.py.
    :param context: str    Human readable description, used by the error message.
    :return: str
    """
    if string_saving_memory is None:
        raise SyntaxError(f"Cannot read {context}: there is no string saving memory.")

    try:
        return string_saving_memory.get_nowait()
    except Empty:
        raise SyntaxError(
            f"Cannot read {context}: the string saving memory is exhausted, "
            "please check the file for an unterminated or misplaced \" literal."
        ) from None


def queue_loader_value(queue_loader: Optional[Queue[str]]) -> str:
    """
    Read the next stored literal, tolerating the plain `None` used by several call sites.

    :param queue_loader: Queue[str] | None
    :return: str
    """
    if queue_loader is None:
        return ""
    return take_saved_string(queue_loader, "string value")


def split_top_level_string(dat_info_string: str, separator: str = ",") -> list[str]:
    """
    Split a string on `separator` while respecting quoted sections and `[{()}]` nesting.

    :param dat_info_string: str    The basic string which you want to split.
    :param separator: str          The split signal.
    :return: list[str]
    """
    parts:       list[str] = []
    buffer:      str       = ""
    depth:       int       = 0
    string_mode: bool      = False
    index:       int       = 0

    while index < len(dat_info_string):
        char: str = dat_info_string[index]

        if char == '"' and not is_escaped_char(dat_info_string, index):
            string_mode = not string_mode
            buffer += char
            index += 1
            continue

        if string_mode:
            buffer += char
            index += 1
            continue

        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth -= 1

        if char == separator and depth == 0:
            parts.append(buffer)
            buffer = ""
            index += 1
            continue

        buffer += char
        index += 1

    parts.append(buffer)
    return parts


def evaluate_stack(value: list[tuple[Any, ctypes.c_uint8]]) -> Any:
    """
    Reduce one value stack (a reverse-polish program stored inside a segment) into its value.

    A token is only treated as an operator when at least two operands are already waiting,
    otherwise a legitimate string value such as "-" would be mistaken for subtraction.

    :param value: list[tuple[Any, ctypes.c_uint8]]
    :return: Any
    """
    stack_load: list[Any] = []

    for item in value:
        if isinstance(item[0], str) and item[0] in CALCULATE_CHAR and len(stack_load) >= 2:
            second_value: Any = stack_load.pop()
            first_value:  Any = stack_load.pop()
            stack_load.append(calculate_dispose(first_value, second_value, item[0]))
        else:
            stack_load.append(item[0])

    if not stack_load:
        return None

    if len(stack_load) > 1:
        raise ValueError(
            "Incomplete expression while the value was reduced: "
            f"{len(stack_load)} operands were left without an operator."
        )

    return stack_load[0]


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
    Locate the first top-level `left_bracket` at or after `right_move` and return its index
    together with the index of the `right_bracket` that closes it.

    IMPORTANT - COORDINATE SYSTEM:
    Both returned indices are ABSOLUTE positions inside the ORIGINAL `dat_info_string` and
    they point AT the two brackets themselves (they were historically mixed: the left one was
    absolute while the right one was relative to a re-sliced string, which silently truncated
    every TABLE/ENUM/UNION type parameter list). Callers therefore always reach the inner
    content with `dat_info_string[left + 1 : right]`.

    Nesting of identical brackets is respected, and quoted sections can be skipped.

    :param dat_info_string: str    The basic string which you want to check.
    :param right_move: int         Start offset, escape the leading part (usually len(keyword)).
    :param left_bracket: str       Opening signal.
    :param right_bracket: str      Closing signal.
    :param string_ignore: bool     Whether quoted content must be skipped.
    :return: tuple[int, int]       (index of left bracket, index of matching right bracket)
    """
    string_signal: bool = False
    depth:         int  = 0
    start_index:   int  = -1

    for index in range(right_move, len(dat_info_string)):
        dat_char: str = dat_info_string[index]

        # Track quoted sections first so escaped content stays invisible for the matcher.
        if dat_char == '"' and not is_escaped_char(dat_info_string, index):
            string_signal = not string_signal
            continue

        if string_signal and string_ignore:
            continue

        # Search the opening bracket.
        if start_index == -1:
            if dat_char == left_bracket:
                start_index = index
                depth = 1
            continue

        # Count the nesting until it closes again.
        if dat_char == left_bracket:
            depth += 1
        elif dat_char == right_bracket:
            depth -= 1
            if depth == 0:
                return start_index, index

    if start_index == -1:
        raise IndexError(f"Cannot find the start signal '{left_bracket}' in the string.")
    raise IndexError(f"Cannot find the end signal '{right_bracket}' in the string.")


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
        # Escape aware: a literal like "\\" ends with a real quote, and a naive "previous char is
        # a backslash" test never closes it, so the closing signal was searched for forever.
        if origin_char == "\"" and not is_escaped_char(origin_string, origin_index):
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


def scalar_value_loader(dat_info_string: str,
                        string_saving_memory: Optional[Queue[str]],
                        context: str = "value") -> Any:
    """
    Load a single typed literal (used by ENUM/LIMIT candidate lists) as a plain python value.

    A quoted literal always costs exactly ONE entry of the string saving memory - never more,
    never zero - so several candidates can't drain the queue and stall the parser.

    :param dat_info_string: str       Raw literal text, e.g. 5 or "yes".
    :param string_saving_memory: Queue[str]   The string saving memory, see parser.py.
    :param context: str               Human readable slot name for error messages.
    :return: Any
    """
    text: str = dat_info_string.strip()

    if len(text) >= 2 and text[0] == '"' and text[-1] == '"':
        return take_saved_string(string_saving_memory, context)

    return complex_data_type_checker(text)[0]


def complex_data_type_checker(dat_info_string: str,
                              string_saving_memory: Optional[Queue[str]] = None) -> tuple[Any, ctypes.c_uint8]:
    """
    Return the parsed value and format signal for a configuration literal.

    A quoted literal always costs ONE entry of the string saving memory when the memory is given:
    every '"' in the source was lifted into it at load time, so leaving the entry behind shifts
    every following statement onto somebody else's string.

    :param dat_info_string: str     Literal text.
    :param string_saving_memory: Queue[str]   Optional string saving memory.
    :return: tuple[Any, ctypes.c_uint8]
    """
    dat_info_string = dat_info_string.strip()
    if not dat_info_string:
        raise ValueError("Unsupported data type.")

    # Quoted strings.
    if len(dat_info_string) >= 2 and dat_info_string[0] == '"' and dat_info_string[-1] == '"':
        target_string = (
            take_saved_string(string_saving_memory, "value")
            if string_saving_memory is not None
            else unescape_string(dat_info_string[1:-1])
        )
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


def int_literal_loader(token: str) -> int:
    """
    Parse one integer token coming from a postfix expression.

    The BOT grammar allows the 0b / 0o / 0d / 0x bases and "_" as a thousand separator, none of
    which the built-in `int()` understands, so every literal goes through the shared scanner.

    :param token: str    The literal token, e.g. "0x1f" or "1_000".
    :return: int
    """
    parsed = _parse_number_literal(token)
    if parsed is None:
        raise ValueError(f"Unsupported integer literal: {token!r}")
    return int(parsed[0])


def decimal_literal_loader(token: str) -> int | float:
    """
    Same loader as int_literal_loader but keeps the fractional part for FLOAT expression lists.

    :param token: str    The literal token, e.g. "0.5" or "0x1f".
    :return: int | float
    """
    parsed = _parse_number_literal(token)
    if parsed is None:
        raise ValueError(f"Unsupported numeric literal: {token!r}")
    return parsed[0]


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
            calculate_stack.append((int_literal_loader(element_item[0]), element_item[1]))

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
            calculate_stack.append((ConversionDecimal(decimal_literal_loader(element_item[0])), element_item[1]))

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
    for saving_item in string_load_list:
        # Operators: merge only when neither side is waiting for a format injection.
        if isinstance(saving_item, str) and saving_item in {"+", "*"}:
            value_search_pointer += 1
            right_string: tuple[str | int, c_uint8] = temp_load_stack.pop()   # right operand first (LIFO)
            left_string:  tuple[str | int, c_uint8] = temp_load_stack.pop()

            if left_string[1] == ValueFormatter.DEFAULT_EMPTY_FORMATTER and right_string[1] == ValueFormatter.DEFAULT_EMPTY_FORMATTER:
                if saving_item == "+" and isinstance(left_string[0], str) and isinstance(right_string[0], str):
                    temp_load_stack.append((left_string[0] + right_string[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER))  # noqa
                elif saving_item == "*" and isinstance(left_string[0], str) and isinstance(right_string[0], int):
                    temp_load_stack.append((left_string[0] * right_string[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER))  # noqa
                elif saving_item == "*" and isinstance(left_string[0], int) and isinstance(right_string[0], str):
                    temp_load_stack.append((right_string[0] * left_string[0], ValueFormatter.DEFAULT_EMPTY_FORMATTER))  # noqa
                else:
                    raise ValueError(f"Error formatter: {left_string[0]} and {right_string[0]}")

            # Or else, just return it as normal, follow LIFO, like nothing happen.
            else:
                temp_load_stack.append(left_string)
                temp_load_stack.append(right_string)
                temp_load_stack.append((saving_item, ValueFormatter.DEFAULT_EMPTY_FORMATTER))

            continue

        # Operands: mark it mutable when it belongs to a FORMAT placeholder slot.
        explain_signal: c_uint8 = ValueFormatter.DEFAULT_EMPTY_FORMATTER
        if explain_search_pointer < len(postfix_inject_index_list):
            if value_search_pointer == postfix_inject_index_list[explain_search_pointer]:
                explain_search_pointer += 1
                explain_signal = ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER

        temp_load_stack.append((saving_item, explain_signal))
        value_search_pointer += 1

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
                if next_search_char == "\"" and not is_escaped_char(value, next_search_index):
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
            "table":            self.table_segment_type_checker,
            "union":            self.union_segment_type_checker,
            "conversion":       self.conversion_segment_type_checker
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
        if key not in CHECKING_DICTIONARY:
            raise KeyError(f"Unsupported configuration data type: {string.strip()!r}")

        return CHECKING_DICTIONARY[key]

    def resolve_type(self, dat_info_string: str) -> tuple[list[type], ctypes.c_uint8]:
        """
        Resolve one type word (with its parameters) into concrete python types.

        `dict_checker` only hands back the *checker callable*, which is what the parser needs
        for the statement level, while every place that needs the real type list (tables,
        unions, nested declarations) must go resolving through this helper instead.

        :param dat_info_string: str    Full type word, e.g. "int" or "table<int, str>".
        :return: tuple[list[type], ctypes.c_uint8]
        """
        return self.dict_checker(dat_info_string)(dat_info_string, None)

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

    def table_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type | list[type]], c_ubyte]:
        """
        Welp...This part of function is used to parse the table type.
        It will return a type value and a format signal, which means the value's type and value's format.
        So from here, it can realize data's type information and make it easy to check it.
        :param queue_loader:
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
        table_element_type_info_string: str = dat_info_string[limit_range[0] + 1 : limit_range[1]]  # noqa

        # Delete the useless value.
        del limit_range

        # So after all is done, we can just return it. Well...don't forget to change it.
        return self._column_type_list(table_element_type_info_string, nested_as_table=True), TypeExplainFormatter.LIST_TYPE_EXPLAIN

    def _column_type_list(self,
                          type_info_string: str,
                          nested_as_table:  bool = False) -> list[type | list[type]]:
        """
        Turn a comma separated type list such as "int, str, table<int, str>" into python types.

        Each column is resolved to a real type instead of the checker callable, otherwise every
        later `isinstance` check silently fails. A column declared as another table collapses
        into a *list* of types, which is exactly the marker `_data_load_table` watches for when
        it has to recurse into a nested table.

        :param type_info_string: str        The inner part of the '<...>' block.
        :param nested_as_table: bool        Keep nested table columns wrapped in a list.
        :return: list[type | list[type]]
        """
        final_saving_list: list[type | list[type]] = []

        for raw_column in split_top_level_string(type_info_string, ","):
            column_word: str = raw_column.strip()
            if column_word == "":
                continue

            column_types, explain = self.resolve_type(column_word)

            if explain == TypeExplainFormatter.LIST_TYPE_EXPLAIN and nested_as_table:
                final_saving_list.append(list(column_types))  # Nested table: a whole signature.
                continue

            if nested_as_table:
                final_saving_list.append(column_types[0] if len(column_types) > 0 else Any)
                continue

            final_saving_list.extend(column_types)  # Union: everything lands in the same pool.

        if len(final_saving_list) == 0:
            raise SyntaxError(f"Empty type list in '{type_info_string.strip()}', table/union need at least one column.")

        return final_saving_list

    def union_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[list[type | list[type]], ctypes.c_uint8]:
        """
        This function will return a type value and a format signal, which means the value's type and value's format.\n
        From the UNION type, is following those rules.\n
        - Start with UNION keyword, use <> to block the detail information.\n
        - Each element in the union is separated by a comma.\n
        - The type of each element is checked individually.\n
        - Result is a list of types, and the format signal is a default type explain.\n
        - Final value's type need to be included in the list.\n
        :param queue_loader:
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
        dat_info_string: str = dat_info_string[limit_range[0] + 1:limit_range[1]]  # noqa

        # Finally, return them.
        return self._column_type_list(dat_info_string, nested_as_table=False), TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

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
        dat_info_string: str = dat_info_string[limit_range[0] + 1 : limit_range[1]]  # noqa

        # ENUM only restricts *which values* are legal, it never changes the storage type,
        # exactly like "-> LIMIT(...)": the candidate list is exposed by `enum_values` and the
        # parser installs it as a limitation rule.
        return [Any], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def enum_values(dat_info_string:    Optional[str],
                    queue_loader:       Optional[Queue[str]]) -> list[Any]:
        """
        Collect every candidate value declared inside ENUM<...>.

        :param dat_info_string: str    Full type word, e.g. "enum<1, 2, 3>".
        :param queue_loader: Queue[str]   The string saving memory, see parser.py.
        :return: list[Any]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")

        dat_info_string = dat_info_string.lower()
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=4  # len("enum") = 4
        )
        inner_string:  str       = dat_info_string[limit_range[0] + 1:limit_range[1]]
        final_saving:  list[Any] = []

        # Start to parse the data.
        for raw_value in split_top_level_string(inner_string, ","):
            temp_saving_string: str = raw_value.strip()
            if temp_saving_string == "":
                continue

            final_saving.append(scalar_value_loader(temp_saving_string, queue_loader, "enum value"))

        if len(final_saving) == 0:
            raise SyntaxError("ENUM<...> needs at least one candidate value.")

        # At last, so we can return them.
        return final_saving

    def conversion_segment_type_checker(self, dat_info_string: Optional[str], queue_loader: Optional[Queue]) -> tuple[
        tuple[list[type], c_ubyte], c_ubyte]:  # noqa
        """

        :param queue_loader:
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
        dat_info_string: str = dat_info_string[limit_range[0] + 1:limit_range[1]]

        # And...Because this only has one segment, so we can just return it.
        del limit_range

        # TODO: the dynamic CONVERSION rule (CONVERSION-START section) is still unimplemented,
        #  see ConfigurationStandalone._data_load_conversion. The declared inner type is used
        #  meanwhile so the statement stays loadable and keeps its static value instead of
        #  blowing the whole file up with an unsupported signal.
        return self.resolve_type(dat_info_string), TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

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
        """
        Return the value parser which belongs to a python type name.\n

        Every returned parser builds a *value stack* (`list[tuple[Any, formatter]]`), which is
        the representation all downstream code expects. `boolean_parser` also serves the
        IDENTIFICATION title lines where a bare bool is wanted, so it stays scalar and is simply
        wrapped here instead.

        :param name: str    Python type name, e.g. 'int', 'str', 'bool'.
        :return: Any    Callable(temp_parse_string, queue_loader[, follow]) -> value stack
        """
        match name:
            case 'int':   return self.int_number_parser     # noqa
            case 'float': return self.float_number_parser   # noqa
            case 'bool':  return self.boolean_stack_parser  # noqa
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
            if element_char == "\"" and not is_escaped_char(temp_parse_string, element_index):
                string_signal = not string_signal

                # The literal goes back into an expression string that is tokenized a second
                # time, so every quote and backslash of the decoded content has to be escaped
                # again - otherwise a decoded '"' silently ends the literal early.
                if not string_signal:
                    escaped_value: str = queue_loader_value(queue_loader).replace("\\", "\\\\").replace("\"", "\\\"")
                    final_saving_string += f"\"{escaped_value}\""

            # Search the operation char. Operators, parentheses and the repeat counter are the
            # only things outside a literal: without the digits a repetition such as "ab" * 3 lost
            # its right operand and the later evaluation popped an empty stack.
            elif not string_signal and (element_char in {"+", "*", "(", ")"} or element_char.isdigit() or element_char.isspace()):
                final_saving_string += element_char

        # All is over, so we can start next part of the parsing, just merge and return the stack here.
        final_saving_string, postfix_inject_index_list = format_checker(final_saving_string)
        return complex_string_suffix_calculator(infix_to_postfix_string(final_saving_string), postfix_inject_index_list)

    @staticmethod
    def boolean_parser(temp_parse_string: str, queue_loader: Optional[Queue[str]], follow: type = Any) -> bool:  # noqa
        return temp_parse_string.lower().strip() == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_TRUE

    @classmethod
    def boolean_stack_parser(cls, temp_parse_string: str, queue_loader: Optional[Queue[str]], follow: type = Any) -> list[tuple[bool, c_ubyte]]:  # noqa
        """
        `boolean_parser` in value-stack form, the representation every segment value uses.

        :param temp_parse_string: str
        :param queue_loader: Queue[str]
        :param follow: type
        :return: list[tuple[bool, c_ubyte]]
        """
        return [(cls.boolean_parser(temp_parse_string, queue_loader), ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

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
        final_saving_list:  list[tuple[Any, ctypes.c_uint8]] = []  # noqa
        type_name:          str                              = value_type.__name__ if hasattr(value_type, "__name__") else str(value_type)  # noqa

        # Split on top level commas instead of hand scanning the characters: quoted commas were
        # previously swallowed into the value and a stray '"' restarted a scan that could never
        # terminate, and a single string candidate used to be read twice.
        for raw_item in split_top_level_string(dat_info_string, ","):
            temp_string_memory: str = raw_item.strip()
            if temp_string_memory == "":
                continue

            # Check the value's prefix to understand what it's mean.
            prefix_temp_saver: ctypes.c_uint8 = ExtensionExplainFormatter.LIMIT_WITHIN_VALUE
            split_memory: list[str] = temp_string_memory.split(None, 1)
            if split_memory[0] == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_EXCLUDE:
                prefix_temp_saver = ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE
                temp_string_memory = split_memory[1].strip() if len(split_memory) > 1 else ""

            if temp_string_memory == "":
                raise SyntaxError("EXCLUDE needs a value in LIMIT(...).")

            # Grammar.bnf: "integer TO integer" is a range and "SUM integer TO integer" folds the
            # whole range into one accumulated value. Both were parsed as an ordinary literal
            # before, which blew up on the word TO.
            range_split: list[str] = temp_string_memory.split()
            if len(range_split) >= 3 and range_split[-2].upper() == keyword.ConfigurationDataExecutiveKeyword.EXECUTIVE_KEYWORD_TO.upper():
                low_value:  Any = int_literal_loader(range_split[-3])
                high_value: Any = int_literal_loader(range_split[-1])

                if len(range_split) == 4 and range_split[0].upper() == keyword.ConfigurationDataExecutiveKeyword.EXECUTIVE_KEYWORD_SUMMARY.upper():
                    # "SUM 1 TO 3" == 1 + 2 + 3.
                    summary_value: int = sum(range(int(low_value), int(high_value) + 1))
                    final_saving_list.append((summary_value, prefix_temp_saver))
                    continue

                range_signal: ctypes.c_uint8 = (
                    ExtensionExplainFormatter.LIMIT_WITHOUT_CONDITION_AND_EQUAL
                    if prefix_temp_saver == ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE
                    else ExtensionExplainFormatter.LIMIT_WITHIN_CONDITION_AND_EQUAL
                )
                final_saving_list.append(((low_value, high_value), range_signal))
                continue

            # A limitation rule compares the value against a plain python value (never against a
            # whole value stack), so every candidate is collapsed to its scalar here.
            final_saving_list.append((self._scalar_limit_value(temp_string_memory, type_name, string_saving_memory), prefix_temp_saver))

        if len(final_saving_list) == 0:
            raise SyntaxError("LIMIT(...) needs at least one value.")

        # So finally, we can return it.
        return final_saving_list

    def _scalar_limit_value(self,
                            dat_info_string:      str,
                            type_name:            str,
                            string_saving_memory: Optional[Queue[str]]) -> Any:
        """
        Build the scalar used by a single LIMIT rule entry.

        :param dat_info_string: str       Already trimmed candidate text.
        :param type_name: str             __name__ of the declared value type.
        :param string_saving_memory: Queue[str]   The string saving memory, see parser.py.
        :return: Any
        """
        # Quoted candidates are strings (or file paths) whatever the declared type is, and they
        # always cost exactly one entry of the string saving memory.
        if len(dat_info_string) >= 2 and dat_info_string[0] == '"' and dat_info_string[-1] == '"':
            return take_saved_string(string_saving_memory, "limit value")

        match type_name:  # Owing to the undeniably profound fact, so in this version, it can't parse complex data like list, database, and so on.
            case "int":   return evaluate_stack(self._value_parser_heap.int_number_parser(dat_info_string, None))           # noqa
            case "float": return float(evaluate_stack(self._value_parser_heap.float_number_parser(dat_info_string, None)))  # noqa
            case "bool":  return self._value_parser_heap.boolean_parser(dat_info_string, None)                              # noqa
            case _:       return complex_data_type_checker(dat_info_string)[0]                                                         # noqa

    @staticmethod
    def regular_rule_explain(dat_info_string: str, string_saving_memory: Queue[str]) -> list[tuple[str, ctypes.c_uint8]]:
        """

        :param string_saving_memory:
        :param dat_info_string: str
        :return: list[tuple[Any, ctypes.c_uint8]]
        """
        dat_info_string:   str                              = dat_info_string.strip()
        final_saving_list: list[tuple[Any, ctypes.c_uint8]] = []

        # One entry per pattern; '!' in front of it flips the rule into "must NOT match".
        for raw_item in split_top_level_string(dat_info_string, ","):
            string_loader: str = raw_item.strip()
            if string_loader == "":
                continue

            regular_signal: c_uint8 = ExtensionExplainFormatter.LIMIT_WITHIN_STRING_REGULAR

            # Search the prefix. Both '!' ("!"^bad$") and the EXCLUDE keyword are accepted; the
            # original scan only advanced the pointer on '"' so anything else spun here forever.
            while True:
                if string_loader.startswith("!"):
                    regular_signal = ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR
                    string_loader = string_loader[1:].strip()
                    continue

                lowered = string_loader.lower()
                if lowered.startswith(ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_EXCLUDE):
                    regular_signal = ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR
                    string_loader = string_loader[len(ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_EXCLUDE):].strip()
                    continue

                break

            # Load regular string from queue. In here, data string just used to check the prefix and count of the string.
            if string_loader.startswith('"'):
                string_loader = take_saved_string(string_saving_memory, "regular expression")

            elif string_loader.endswith('"'):  # tolerate a stray closing quote
                string_loader = string_loader[:-1]

            if string_loader == "":
                raise SyntaxError("REGULAR(...) got an empty pattern.")

            final_saving_list.append((string_loader, regular_signal))

        if len(final_saving_list) == 0:
            raise SyntaxError("REGULAR(...) needs at least one pattern.")

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
