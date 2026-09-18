import re
from dataclasses import dataclass
from typing import Final, Optional

from src.parsecheck.syntax.errors import BOTSyntaxError


# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> LEXICAL TOKEN DEFINITION.
#
# INTRODUCE SENTENCE.
# -> The BOT language is case insensitive outside of string literals and every word may carry a
#    dash inside (DATABASES-START, FANTASTIC-2, LOAD-INT), so the lexer cannot be the usual
#    "letters and digits" scanner - it has to decide whether a dash joins the word in front of it
#    or acts as the "->" arrow / minus operator.
# -> Everything the parser needs later (error positions especially) depends on tokens keeping their
#    original offset, therefore each token remembers where it started in the untouched source.
#
# GLOBAL VALUE SEGMENT START.


class TokenType(object):
    # +------------------+---------------+------------------------------------------------+
    # |       NAME       |     VALUE     |                     EXPLAIN                    |
    # +------------------+---------------+------------------------------------------------+
    IDENT:   Final[str] = "identifier"   # Is a word such as a name, a keyword or a type name.
    NUMBER:  Final[str] = "number"       # 42, 1.0, 0x0A, 0b1011, 1_000 ...
    STRING:  Final[str] = "string"       # A double quoted literal, escapes already resolved.
    CHAR:    Final[str] = "char"         # A single quoted literal such as 'C'.
    OP:      Final[str] = "operator"     # Any punctuation listed in OPERATOR_TABLE.
    EOF:     Final[str] = "end-of-file"  # The synthetic token closing the stream.
    # +------------------+---------------+------------------------------------------------+


@dataclass(frozen=True)
class Token(object):
    """
    One lexical unit of a configuration file.

    :param kind:   str   TokenType value.
    :param value:  str   Payload (for a string it is the *decoded* content).
    :param offset: int   0-based offset inside the untouched source.
    :param raw:    str   The exact slice of source this token came from.
    """
    kind:   str
    value:  str
    offset: int
    raw:    str

    @property
    def word(self) -> str:
        """
        Case folded payload, the way keywords have to be compared.
        :return: str
        """
        return self.value.lower()

    def is_operator(self, *values: str) -> bool:
        """:return: bool   True when this token is any of the given operators."""
        return self.kind == TokenType.OP and self.value in values

    def is_word(self, *words: str) -> bool:
        """:return: bool   True when this token is any of the given keywords (case insensitive)."""
        return self.kind == TokenType.IDENT and self.word in {word.lower() for word in words}

    def describe(self) -> str:
        """Human readable form used inside error messages."""
        if self.kind == TokenType.EOF:
            return "end of file"

        if self.kind == TokenType.STRING:
            return f"string {self.raw!r}"

        return f"'{self.raw}'" if self.kind == TokenType.OP else f"{self.raw!r}"


# Multi character operators first: the scanner must never eat ">>" as two ">" shifts.
OPERATOR_TABLE: Final[tuple[str, ...]] = (
    "->", "**", "//", "<<", ">>", "<=", ">=", "==", "!=", "&&", "||",
    "[", "]", "(", ")", "{", "}", ",", ";", ".", "=", "<", ">", "+", "-", "*", "/", "&", "|", "^", "!", "%", ":",
)

WHITESPACE:        Final[str] = " \t\r\n\f\v"
LINE_COMMENT:      Final[str] = "#"

# Those two are used *inside* the parser as sentinels (see ReplacerDatabase), so they must never
# show up in a source file - otherwise a string could smuggle itself out of its own quotes.
FORBIDDEN_CHARACTER: Final[tuple[str, ...]] = ("\uFFFF", "\uFFFE")

# Control characters are rejected outright, they can only ever be a copy/paste accident.
_ALLOWED_CONTROL:    Final[tuple[str, ...]] = ("\t", "\n", "\r")

_DECIMAL_PATTERN: Final[re.Pattern] = re.compile(r"^(?:0d)?\d[\d_]*(?:\.\d[\d_]*)?$", re.IGNORECASE)
_HEX_PATTERN:     Final[re.Pattern] = re.compile(r"^0x[0-9a-f][0-9a-f_]*$", re.IGNORECASE)
_BINARY_PATTERN:  Final[re.Pattern] = re.compile(r"^0b[01][01_]*$", re.IGNORECASE)
_OCTAL_PATTERN:   Final[re.Pattern] = re.compile(r"^0o[0-7][0-7_]*$", re.IGNORECASE)

_NUMBER_STARTER:  Final[str] = "0123456789"


# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION FUNCTION PART. TO >>> LEXICAL SCANNER.
#
# CODE SEGMENT START.


def tokenize(source: str) -> list[Token]:
    """
    Split a whole configuration source into tokens.

    Comments are dropped here, string literals are decoded here, and every structural mistake that
    can already be spotted character by character (unterminated literal, stray character, broken
    numeric literal) is raised from here with a precise position.

    :param source: str   Untouched configuration source.
    :return: list[Token]      Tokens with a synthetic EOF token appended at the end.
    """
    _reject_forbidden_character(source)

    tokens:  list[Token] = []
    index:   int         = 0
    length:  int         = len(source)

    while index < length:
        char: str = source[index]

        if char in WHITESPACE:
            index += 1
            continue

        if char == LINE_COMMENT:
            while index < length and source[index] != "\n":
                index += 1
            continue

        if char == '"':
            index = _scan_string(source, index, tokens)
            continue

        if char == "'":
            index = _scan_char(source, index, tokens)
            continue

        if char in _NUMBER_STARTER or (char == "." and index + 1 < length and source[index + 1].isdigit()):
            index = _scan_number(source, index, tokens)
            continue

        if char.isalpha() or char == "_":
            index = _scan_identifier(source, index, tokens)
            continue

        operator: Optional[str] = _match_operator(source, index)
        if operator is not None:
            tokens.append(Token(TokenType.OP, operator, index, operator))
            index += len(operator)
            continue

        raise BOTSyntaxError(
            f"Illegal character {char!r} outside of a string literal.",
            offset=index,
            source=source,
            token=char,
        )

    tokens.append(Token(TokenType.EOF, "", length, ""))
    return tokens


def _reject_forbidden_character(source: str) -> None:
    """
    Reject characters that would corrupt the parser itself.

    U+FFFF and U+FFFE are the two transient markers the parser swaps in for a quote and for a
    semicolon inside a string. See `ReplacerDatabase`.
    """
    for index, char in enumerate(source):
        if char in FORBIDDEN_CHARACTER:
            raise BOTSyntaxError(
                f"Found illegal character U+{ord(char):04X} at offset {index}, please make sure there is no "
                f"\\uFFFF or \\uFFFE in the string - both are reserved by the parser.",
                offset=index,
                source=source,
                token=char,
            )

        if ord(char) < 0x20 and char not in _ALLOWED_CONTROL:
            raise BOTSyntaxError(
                f"Found control character U+{ord(char):04X} at offset {index}, control characters are not allowed "
                f"outside of a string literal.",
                offset=index,
                source=source,
                token=char,
            )


def _match_operator(source: str, index: int) -> Optional[str]:
    """:return: Optional[str]   The longest operator starting at index, None when there is none."""
    for operator in OPERATOR_TABLE:
        if source.startswith(operator, index):
            return operator
    return None


def _scan_identifier(source: str, index: int, tokens: list[Token]) -> int:
    """
    Scan one word.

    A dash continues the word only when it is directly followed by another word character, which is
    what makes "DATABASES-START" one token while "x -> y" stays three.
    """
    start: int = index
    length: int = len(source)

    index += 1
    while index < length:
        char: str = source[index]

        if char.isalnum() or char == "_":
            index += 1
            continue

        if char == "-" and index + 1 < length:
            follower: str = source[index + 1]
            if follower.isalnum() or follower == "_":
                index += 1
                continue

        break

    raw: str = source[start: index]
    tokens.append(Token(TokenType.IDENT, raw, start, raw))
    return index


def _scan_number(source: str, index: int, tokens: list[Token]) -> int:
    """Scan and validate one numeric literal."""
    start: int = index
    length: int = len(source)

    index += 1
    while index < length:
        char: str = source[index]
        if char.isalnum() or char in ("_", "."):
            index += 1
            continue
        break

    raw: str = source[start: index]

    if not (_DECIMAL_PATTERN.match(raw) or _HEX_PATTERN.match(raw)
            or _BINARY_PATTERN.match(raw) or _OCTAL_PATTERN.match(raw)):
        raise BOTSyntaxError(
            f"Malformed numeric literal {raw!r}.",
            offset=start,
            source=source,
            token=raw,
            hint="Allowed forms are 1234, 1.25, 0xFF, 0b1011, 0o17, 0d99 and digit separators like 1_000.",
        )

    tokens.append(Token(TokenType.NUMBER, raw, start, raw))
    return index


def _scan_string(source: str, index: int, tokens: list[Token]) -> int:
    """Scan a double quoted literal and decode its escape sequences."""
    length: int = len(source)
    start:  int = index

    index += 1  # Drop the opening quote.
    buffer: list[str] = []

    while index < length:
        char: str = source[index]

        if char == "\\":
            if index + 1 >= length:
                raise BOTSyntaxError(
                    "Truncated escape sequence at the end of the file.",
                    offset=index,
                    source=source,
                    token=char,
                )
            follower: str = source[index + 1]
            buffer.append(_decode_escape(follower, index, source))
            index += 2
            continue

        if char == '"':
            tokens.append(Token(TokenType.STRING, "".join(buffer), start, source[start: index + 1]))
            return index + 1

        if char == "\n":
            raise BOTSyntaxError(
                "Unterminated string literal, a string may not cross a line break.",
                offset=start,
                source=source,
                token=source[start: min(start + 24, length)],
                hint='Close the literal with a " or escape the line break.',
            )

        buffer.append(char)
        index += 1

    raise BOTSyntaxError(
        "Unterminated string literal, reached the end of the file while inside a string.",
        offset=start,
        source=source,
        token=source[start: min(start + 24, length)],
        hint='Every " has to be closed before the file ends (use \\" for a literal quote).',
    )


def _scan_char(source: str, index: int, tokens: list[Token]) -> int:
    """Scan a single quoted literal such as 'C'."""
    length: int = len(source)
    start:  int = index

    index += 1
    buffer: list[str] = []

    while index < length:
        char: str = source[index]

        if char == "\\":
            if index + 1 >= length:
                raise BOTSyntaxError(
                    "Truncated escape sequence at the end of the file.",
                    offset=index,
                    source=source,
                    token=char,
                )
            buffer.append(_decode_escape(source[index + 1], index, source))
            index += 2
            continue

        if char == "'":
            if len(buffer) == 0:
                raise BOTSyntaxError(
                    "Empty character literal, at least one character is required between the quotes.",
                    offset=start,
                    source=source,
                    token=source[start: index + 1],
                )
            tokens.append(Token(TokenType.CHAR, "".join(buffer), start, source[start: index + 1]))
            return index + 1

        if char == "\n":
            raise BOTSyntaxError(
                "Unterminated character literal, reached the line break before the closing quote.",
                offset=start,
                source=source,
                token=source[start: index],
            )

        buffer.append(char)
        index += 1

    raise BOTSyntaxError(
        "Unterminated character literal, reached the end of the file while looking for a closing quote.",
        offset=start,
        source=source,
        token=source[start: min(start + 24, length)],
    )


def _decode_escape(follower: str, index: int, source: str) -> str:
    """:return: str   The real character behind one escape sequence."""
    escape_table: dict[str, str] = {
        "\\": "\\", "'":  "'",  '"':  '"',
        "r":  "\r", "n":  "\n", "a":  "\a", "b": "\b",
        "f":  "\f", "t":  "\t", "v":  "\v", "0": "\0",
    }

    if follower in escape_table:
        return escape_table[follower]

    raise BOTSyntaxError(
        f"Unsupported escape sequence '\\{follower}'.",
        offset=index,
        source=source,
        token=f"\\{follower}",
        hint="Supported escapes are \\\\ \\' \\\" \\r \\n \\a \\b \\f \\t \\v \\0.",
    )


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
