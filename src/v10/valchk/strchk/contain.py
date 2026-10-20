def brackets_edge_index_checker(dat_info_string: str,
                                right_move:      int,
                                left_bracket:    str  = "<",
                                right_bracket:   str  = ">") -> tuple[int, int]:
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
    :param left_bracket: str       Opening signal set.
    :param right_bracket: str      Closing signal set.
    :return: tuple[int, int]       (index of left bracket, index of matching right bracket)
    """
    depth:         int  = 0
    start_index:   int  = -1

    for index in range(right_move, len(dat_info_string)):
        dat_char: str = dat_info_string[index]

        # Search the opening bracket.
        if start_index == -1:
            if dat_char in left_bracket:
                start_index = index
                depth = 1
            continue

        # Count the nesting until it closes again.
        if dat_char in left_bracket:
            depth += 1
        elif dat_char in right_bracket:
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
    deep_signal:   int  = 0

    # Start the loop.
    for origin_index, origin_char in enumerate(origin_string):
        if origin_char == signal_start:
            deep_signal += 1
        elif origin_char == signal_end:
            deep_signal -= 1
            if deep_signal == 0:
                return origin_index
    raise IndexError("Cannot find the correct edge of the signal.")


def search_first_end_legal_char(string: str, char: str) -> int:
    """
    A fix function, search the correct first value.
    :param string:
    :param char:
    :return: int
    """
    for index, str_char in enumerate(string):
        if str_char == char:
            return index
    return -1


def split_top_level_statements_static(s: str) -> list[str]:
    parts:       list[str] = []
    buf:         str = ''
    depth:       int = 0
    i:           int = 0

    # Start the loop to check the ';' to split sentence in here.
    while i < len(s):
        ch = s[i]
        if ch in '{[(':
            depth += 1
        elif ch in '}])':
            depth -= 1
        if ch == ';' and depth == 0:
            parts.append(buf.strip())
            buf = ''
            i += 1
            continue
        buf += ch
        i += 1
    if buf.strip() != '':
        parts.append(buf.strip())
    return parts
