from src.v10.struct.char import ESCAPE_SEQUENCE_DICT


def is_escaped_char(base_string: str | list[str], index: int) -> bool:
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


def rebuild_escape(string_content: str) -> str:
    """
    This function is used to replace the escape char.
    :param string_content: Target string content.
    :return: str
    """
    new_string: str = ""
    scan_index: int = 0
    while scan_index < len(string_content):
        if string_content[scan_index] == "\\":
            backslash_run: int = 0
            while scan_index < len(string_content) and string_content[scan_index] == "\\":
                scan_index += 1
                backslash_run += 1
                if backslash_run == 2:
                    backslash_run = 0
                    new_string += "\\"
            if backslash_run == 1:
                if scan_index == len(string_content):
                    raise SyntaxError("Not a legal string: " + string_content)
                if string_content[scan_index] in "bodx":    # noqa
                    new_string += ESCAPE_SEQUENCE_DICT["\\" + string_content[scan_index: scan_index + 3]]
                    scan_index += 2
                else:
                    new_string += ESCAPE_SEQUENCE_DICT["\\" + string_content[scan_index]]
        else:
            new_string += string_content[scan_index]
        scan_index += 1
    return new_string
