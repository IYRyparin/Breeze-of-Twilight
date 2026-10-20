from src.v10.valchk.strchk.escape import is_escaped_char


def split_top_level_string(dat_info_string: str, separator: str = ",") -> list[str]:
    """
    Split a string on `separator` while respecting quoted sections and `[{(<>)}]` nesting.

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

        if char in "{[(<":
            depth += 1
        elif char in "}])>":
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
