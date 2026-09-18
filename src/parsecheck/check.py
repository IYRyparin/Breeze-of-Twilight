from src.parsecheck.syntax.errors import BOTSyntaxError
from src.parsecheck.syntax.tokens import Token, TokenType, tokenize
from src.parsecheck.syntax.validator import SyntaxValidator, validate_syntax


# ----- SOURCE START -----
#
# region
# IDENTIFICATION FUNCTION PART. TO >>> CONFIGURATION PRE-PARSE CHECKER.
#
# INTRODUCE SENTENCE.
# -> This module is the gate every configuration has to walk through before the parser sees a
#    single character. `start_check` is called at the very top of ConfigurationStandalone.__init__,
#    so everything it rejects can never reach the parser and can therefore never turn into one of
#    those "IndexError three layers deep" failures again.
# -> The real work lives in the `src/parsecheck/syntax` package:
#      * tokens.py      - lexical scanner (comments, literals, numbers, operators).
#      * validator.py   - recursive descent validator following grammar/Grammar.bnf, corrected
#                         against grammar/example.bot, which is the reference version.
#      * errors.py      - BOTSyntaxError, carrying line, column and the offending source line.
# -> Nothing here builds data: a correct file falls straight through, anything else raises.
#
# CODE SEGMENT START.


def start_check(string: str) -> None:
    """
    Validate the whole syntax of a BOT configuration source.

    Called by ConfigurationStandalone.__init__ before any parsing happens. The signature stays
    exactly what it always was: take the source, return nothing, raise on the first mistake.

    :param string: str   Untouched configuration source.
    :return: None
    """
    if "\xFF\xFF" in string or "\xFF\xFE" in string:
        raise ValueError("Found illegal value in here, please make sure there is no \uFFFF or \uFFFE in the stirng.")  # noqa

    validate_syntax(string)


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION FUNCTION PART. TO >>> VALUE FORM PREDICATE.
#
# INTRODUCE SENTENCE.
# -> Those helpers answer one question about a *fragment* of configuration text: "is this written
#    like <form>?" They are the public form of the checks the validator uses internally, and they
#    never raise - they answer with True or False so a caller can build its own error message.
# -> A fragment counts as one form only when it is *exactly* one token of that form, therefore
#    "1 + 1" is not an int while "0x0A" is.
#
# CODE SEGMENT START.


def _tokenize_fragment(string: str) -> list[Token]:
    """
    :return: list[Token]   Tokens of one value fragment (comments allowed, they are dropped).
    """
    return tokenize(string)


def _is_exactly(string: str, predicate) -> bool:
    try:
        tokens: list[Token] = _tokenize_fragment(string)
    except BOTSyntaxError:
        return False

    payload: list[Token] = [token for token in tokens if token.kind != TokenType.EOF]
    return len(payload) == 1 and predicate(payload[0])


def check_is_int(string: str) -> bool:
    """:return: bool   True when the fragment is a single integer literal (42, 0x0A, 0b1011, 1_000)."""
    def predicate(token: Token) -> bool:
        # Every whole number form is an int: 42, 0x1F, 0b1011, 0o17, 0d99 and 1_000.
        return token.kind == TokenType.NUMBER and "." not in token.value

    return _is_exactly(string, predicate)


def check_is_float(string: str) -> bool:
    """:return: bool   True when the fragment is a single decimal literal (1.0, .5, 0.9)."""
    def predicate(token: Token) -> bool:
        return token.kind == TokenType.NUMBER and "." in token.value

    return _is_exactly(string, predicate)


def check_is_bool(string: str) -> bool:
    """:return: bool   True when the fragment is TRUE or FALSE (any writing case)."""
    def predicate(token: Token) -> bool:
        return token.kind == TokenType.IDENT and token.word in ("true", "false")

    return _is_exactly(string, predicate)


def check_is_table(string: str) -> bool:
    """
    :return: bool   True when the fragment is a bracketed row list such as [(1, "a"), (2, "b")].
    """
    def predicate(token: Token) -> bool:
        return token.kind == TokenType.OP and token.value in ("[", "(")

    try:
        tokens: list[Token] = _tokenize_fragment(string)
    except BOTSyntaxError:
        return False

    payload: list[Token] = [token for token in tokens if token.kind != TokenType.EOF]

    if len(payload) < 2 or not predicate(payload[0]):
        return False

    # A table opens with '[' and closes with ']'; anything else is just an expression.
    return payload[0].value == "[" and payload[-1].is_operator("]")


def check_is_database(string: str) -> bool:
    """:return: bool   True when the fragment is a brace block such as { NAME [INT] CST = 1; }."""
    try:
        tokens: list[Token] = _tokenize_fragment(string)
    except BOTSyntaxError:
        return False

    payload: list[Token] = [token for token in tokens if token.kind != TokenType.EOF]

    if len(payload) < 2:
        return False

    return payload[0].is_operator("{") and payload[-1].is_operator("}")


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION CLASS PART. TO >>> TRANSIENT CHARACTER TABLE.
#
# INTRODUCE SENTENCE.
# -> The parser cannot keep a quote or a semicolon inside a string, because those two characters
# -> are the structural markers of the language itself. It therefore swaps them for two code points
# -> that can never appear elsewhere and swaps them back when the string is read.
# -> Because those two code points are reserved for that trick, the tokenizer rejects them in a
# -> source file - see tokens.FORBIDDEN_CHARACTER.
#
# CODE SEGMENT START.


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


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION CLASS PART. TO >>> SYNTAX CHECKER FACADE.
#
# INTRODUCE SENTENCE.
# -> The object form of the module level checker. It keeps its `data` source so several questions
# -> can be asked about one file, and `check` is the same operation as `start_check`.
#
# CODE SEGMENT START.


class SyntaxChecker(object):
    def __init__(self, data: str) -> None:
        self._data: str = data

    @property
    def data(self) -> str:
        """:return: str   The source this checker was built on."""
        return self._data

    def check(self) -> None:
        """
        Validate the source held by this checker.
        :raise BOTSyntaxError: With line, column and snippet on the first syntax error.
        :return: None
        """
        start_check(self._data)

    def tokens(self) -> list[Token]:
        """:return: list[Token]   The token stream, useful when debugging a grammar change."""
        return tokenize(self._data)

    def is_int(self, string: str) -> bool:      return check_is_int(string)      # noqa
    def is_float(self, string: str) -> bool:    return check_is_float(string)    # noqa
    def is_bool(self, string: str) -> bool:     return check_is_bool(string)     # noqa
    def is_table(self, string: str) -> bool:    return check_is_table(string)    # noqa
    def is_database(self, string: str) -> bool: return check_is_database(string) # noqa


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
