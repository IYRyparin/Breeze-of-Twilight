def start_check(string: str) -> None:
    if "\xFF\xFF" in string or "\xFF\xFE" in string:
        raise ValueError("Found illegal value in here, please make sure there is no \uFFFF or \uFFFE in the stirng.")


def check_is_int(string: str) -> bool:
    ...


def check_is_float(string: str) -> bool:
    ...


def check_is_bool(string: str) -> bool:
    ...


def check_is_table(string: str) -> bool:
    ...


def check_is_database(string: str) -> bool:
    ...


class ReplacerDatabase(object):
    SPECIAL_CHARACTER_REPLACER_DICT: dict[str, str] = {
        "\uFFFF": "\"", "\uFFFE": ";",  # noqa
        "\\\\":   "\\",
        "\\'":    "'",
        "\\\"": "\"",
        "\\r": "\r", "\\n": "\n", "\\a": "\a", "\\b": "\b", "\\f": "\f", "\\t": "\t", "\\v": "\v",
    }
    PATTERN_REGEX_STRING: str = (r'^\^(?(DEFINE)(?<literal>[^\\\[(){}|*+?$^])(?<escape>\\.)(?<class>\[(?:[^\\\]]+|\\.)*\])'
                                 r'(?<group>\((?:\\?:|\\?<[^>]+>|\\?=|\\?!|\\?<=|\\?<!)?(?&internal)\))(?<atom>(?&literal)|'
                                 r'(?&escape)|(?&class)|(?&group))(?<quantifier>[*+?]|\{\d+(?:,\d*)?\})(?<item>(?&atom)'
                                 r'(?&quantifier)?)(?<branch>(?&item)*)(?<internal>(?&branch)(?:\|(?&branch))*))(?&internal)\$$')

    """
    STRING_CHARACTER_REPLACER: dict[str, str] = {}
    STRING_CHARACTER_REPLACER.update({
        f"\\x{i:02x}": chr(i)
        for i in range(0x00, 0x100)
    })
    STRING_CHARACTER_REPLACER.update({
        f"\\u{i:04x}": chr(i)
        for i in range(0x0000, 0x10000)
    })
    """


class SyntaxChecker(object):
    def __init__(self, data: str) -> None:
        self._data: str = data
