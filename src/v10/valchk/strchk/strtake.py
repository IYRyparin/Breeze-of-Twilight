from typing import Optional
from queue import Queue, Empty

from src.v10.valchk.strchk.escape import is_escaped_char, rebuild_escape
from src.v10.struct.signal import ValueFormatter


def take_saved_string(string_saving_memory: Optional[Queue[tuple[str, int]]]) -> tuple[str, int]:
    """
    Pull one pre-decoded string out of the saving memory.

    Every `"..."` literal inside a BOT file is extracted up-front into this queue and is meant
    to be consumed exactly once, in source order. Using the blocking `Queue.get()` here means
    ANY misalignment (a doubled read, a synthesized literal, an unterminated quote) makes the
    parser hang forever with no diagnostics at all, so reads are always non-blocking and an
    exhausted queue is reported as a syntax problem instead.

    :param string_saving_memory: Queue[str]   The string saving memory, see parser.py.
    :return: str
    """
    if string_saving_memory is None:
        raise SyntaxError("Cannot read string literal: there is no string saving memory.")
    try:
        return string_saving_memory.get_nowait()
    except Empty:
        raise SyntaxError(
            "Cannot read string literal: the string saving memory is exhausted, "
            "please check the file for an unterminated or misplaced \" literal."
        ) from None


def load_string_saving_queue(config_string: str) -> tuple[Queue[tuple[str, int]], str]:
    """
    In here, this function is used to check and load the string.
    When we try to lower the string, we may break the origin char.
    To save them, so we need to check it before lower all value.
    :return: list[str]
    """
    # +----------+------+-------+--------------------+
    # |   NAME   | TYPE | VALUE |      EXPLAIN       |
    # +----------+------+-------+--------------------+
    string_signal: bool = False  # Signal in string or not.
    input_signal: bool = True  # Signal in announcement or not.
    basic_string: str = ""  # String which is changed.
    # +----------+------+-------+--------------------+

    # Start the basic check, push out the string value and save it into temp list.
    for index, char in enumerate(config_string):
        if char == "\"" and not is_escaped_char(config_string, index):
            string_signal = not string_signal

        # When we find the announcement signal, we need to change the signal to True, and then we can start to drop the announcement part.
        elif char == "\n" and not input_signal:
            input_signal = True
            continue

        # When we in the string part, so it means that we don't need to care about the data, just drop it off.
        if not input_signal:
            continue

        # Or anything else, we need to check out the announcement signal, and then we can start to parse it.
        else:
            if char == "#" and not string_signal:
                input_signal = False

            # On other part, we can just add the signal into the string.
            else:
                basic_string += char

    # Export the basic value which maybe used when parsing the data, even though their value just is NoneType.
    # +----------------------------+----------------------+-----------------------+----------------------+
    # |            NAME            |         TYPE         |          VALUE        |       EXPLAIN        |
    # +----------------------------+----------------------+-----------------------+----------------------+
    _is_string_signal:         bool                   = False    # A boolean signal which used to explain this part is in string or not.
    _temp_memory_string:       str                    = ""       # A temp value, used to save the string.
    _temp_memory_string_saver: Queue[tuple[str, int]] = Queue()  # We need to save the string, or it will be broken.
    _final_return_string:      str                    = ""       # Final string which changed and easy to parse.
    # +----------------------------+----------------------+-----------------------+----------------------+

    # Start the basic check, push out the string value and save it into temp list.
    for index, one_char in enumerate(basic_string):
        _is_escaped: bool = is_escaped_char(basic_string, index)
        if one_char == "\"" and not _is_escaped:  # To index the setter, we need to make sure it is not out of range.
            _is_string_signal = not _is_string_signal
            _final_return_string += "\""

            # When this value change True to False, means it is go out to string right now.
            if not _is_string_signal:  # Before to save it, we must replace the special part in here.
                _temp_memory_string_saver.put((rebuild_escape(_temp_memory_string), ValueFormatter.DEFAULT_STRING_FORMATTER))
                _temp_memory_string = ""  # Flush the temp string for prepare to the next string value.

        # If it is in the string, we need to start to push the string into the saving value.
        elif _is_string_signal and one_char is not None:
            _temp_memory_string += one_char

        # Not in the string, we can input it to the final return data's string.
        elif not _is_string_signal and one_char is not None:
            _final_return_string += one_char

    # An unterminated quote means the file itself is broken: report it now instead of
    # letting every later statement silently steal someone else's string.
    if _is_string_signal:
        raise SyntaxError("Unterminated string literal, please check the \" signals in the file.")
    return _temp_memory_string_saver, _final_return_string.lower()
