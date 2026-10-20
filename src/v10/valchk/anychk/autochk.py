from typing import Any, Optional
from queue import Queue

from src.v10.struct import kword
from src.v10.struct.signal import ValueFormatter
from src.v10.valchk.strchk.escape import rebuild_escape
from src.v10.valchk.strchk.rechk import is_file_string_literal
from src.v10.valchk.strchk.numcheck import parse_number_literal
from src.v10.valchk.strchk.strtake import take_saved_string


def scalar_value_loader(dat_info_string: str,
                        string_saving_memory: Optional[Queue[tuple[str, int]]]) -> Any:
    """
    Load a single typed literal (used by ENUM/LIMIT candidate lists) as a plain python value.

    A quoted literal always costs exactly ONE entry of the string saving memory - never more,
    never zero - so several candidates can't drain the queue and stall the parser.

    :param dat_info_string: Raw literal text, e.g. 5 or "yes".
    :param string_saving_memory: The string saving memory, see parser.py.
    :return: Any
    """
    text: str = dat_info_string.strip()
    if len(text) >= 2 and text[0] == '\"' and text[-1] == '\"':
        return take_saved_string(string_saving_memory)
    return complex_data_type_checker(text)[0]


def complex_data_type_checker(dat_info_string: str,
                              string_saving_memory: Optional[Queue[tuple[str, int]]] = None) -> tuple[Any, int]:
    """
    Return the parsed value and format signal for a configuration literal.

    A quoted literal always costs ONE entry of the string saving memory when the memory is given:
    every '"' in the source was lifted into it at load time, so leaving the entry behind shifts
    every following statement onto somebody else's string.

    :param dat_info_string: Literal text.
    :param string_saving_memory: Optional string saving memory.
    :return: tuple[Any, int]
    """
    dat_info_string = dat_info_string.strip()

    # 1. Quoted strings.
    if len(dat_info_string) >= 2 and dat_info_string[0] == '"' and dat_info_string[-1] == '"':
        target_string = (
            take_saved_string(string_saving_memory)[0]
            if string_saving_memory is not None
            else rebuild_escape(dat_info_string[1:-1])
        )
        if is_file_string_literal(target_string):
            return str(target_string), ValueFormatter.FILE_STRING_FORMATTER
        return str(target_string), ValueFormatter.DEFAULT_STRING_FORMATTER

    # 2. Boolean and null keywords.
    lowered = dat_info_string.lower()
    if lowered == kword.ConfigurationValueReplacerKeyword.TRUE:
        return True, ValueFormatter.KEYWORD_SIGNAL_FORMATTER
    if lowered == kword.ConfigurationValueReplacerKeyword.FALSE:
        return False, ValueFormatter.KEYWORD_SIGNAL_FORMATTER
    if lowered == kword.ConfigurationValueReplacerKeyword.NULL:
        return None, ValueFormatter.KEYWORD_SIGNAL_FORMATTER

    # 3. Numeric literals.
    numeric_value = parse_number_literal(dat_info_string)
    if numeric_value is not None:
        return numeric_value

    # 4. Container literals.
    if (
        (dat_info_string.startswith("[") and dat_info_string.endswith("]"))
        or (dat_info_string.startswith("{") and dat_info_string.endswith("}"))
        or (dat_info_string.startswith("(") and dat_info_string.endswith(")"))
        or (dat_info_string.startswith("<") and dat_info_string.endswith(">"))
    ):
        try:
            ...  # TODO: Fix the container literal parsing logic here.
        except (SyntaxError, ValueError):
            pass

    # Not the supported type, we can raise the exception in here.
    raise ValueError("Unsupported data type.")
