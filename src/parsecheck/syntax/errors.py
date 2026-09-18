from typing import Final, Optional


# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL EXCEPTION. TO >>> SYNTAX CHECKER ERROR.
#
# INTRODUCE SENTENCE.
# -> Every syntax error found by the pre-parse checker is reported through this single class.
# -> It inherits from the built-in SyntaxError on purpose: the parser and everything on top of it
# -> already catch SyntaxError, so a broken configuration aborts exactly the same way it used to,
# -> only now with a precise position instead of an IndexError raised three layers deeper.
# -> Besides the message it carries everything needed to print a compiler-like diagnostic:
# -? line, column, the offending source line and a caret under the mistake.
#
# CODE SEGMENT START.


class BOTSyntaxError(SyntaxError):
    """
    A syntax error located inside a BOT configuration source.

     - attr line:     int     1-based line number of the mistake (-1 when unknown).
     - attr column:   int     1-based column number of the mistake (-1 when unknown).
     - attr offset:   int     0-based character offset inside the whole source (-1 when unknown).
     - attr source:   str     The original configuration source.
     - attr snippet:  str     The offending source line, stripped of its line break.
     - attr hint:     str     An optional "did you mean" style suggestion.
    """

    def __init__(self,
                 message: str,
                 offset:  Optional[int] = None,
                 source:  Optional[str] = None,
                 hint:    Optional[str] = None,
                 token:   Optional[str] = None) -> None:
        # +----------+---------------------+---------------------------------------+
        # |   NAME   |         TYPE        |                   VALUE               |
        # +----------+---------------------+---------------------------------------+
        self.message: Final[str]           = message
        self.source:  Final[Optional[str]] = source
        self.offset:  Final[int]           = offset if offset is not None else -1
        self.hint:    Final[Optional[str]] = hint
        self.token:   Final[Optional[str]] = token
        self.line:    int                  = -1
        self.column:  int                  = -1
        self.snippet: str                  = ""
        # +----------+---------------------+---------------------------------------+

        if source is not None and self.offset >= 0:
            self.line, self.column, self.snippet = self._locate(source, self.offset)

        # Built-in SyntaxError also understands (msg, (filename, lineno, offset, text)).
        super().__init__(self._render())

    # ----- SOURCE LINE LOOKUP -----
    #
    # INTRODUCE SENTENCE.
    # -> Turn a raw character offset into a human-readable line / column pair. The line breaks are
    #    handled for both the Unix and the Windows flavor, because a configuration written on
    #    Windows still has to report the same line number as the editor shows.
    #
    # CODE SEGMENT START.

    @staticmethod
    def _locate(source: str, offset: int) -> tuple[int, int, str]:
        """
        Map a raw character offset onto a (line, column, snippet) triple.

        :param source: str    Whole configuration source.
        :param offset: int    0-based character offset of the mistake.
        :return: tuple[int, int, str]
        """
        consumed: int = 0

        for line_index, raw_line in enumerate(source.splitlines(keepends=True), start=1):
            if offset < consumed + len(raw_line):
                head:   str = raw_line[: offset - consumed].expandtabs(4)
                snippet: str = raw_line.rstrip("\r\n").expandtabs(4)
                return line_index, len(head) + 1, snippet

            consumed += len(raw_line)

        # Out of range (can only happen on a malformed offset): fall back to the last line.
        last_line: str = source.splitlines()[-1].expandtabs(4) if source else ""
        return -1, -1, last_line

    # CODE SEGMENT END.
    # endregion
    #
    # ----- SEPARATING LINE -----

    def _render(self) -> str:
        """
        Build the multi line diagnostic that is printed when the exception is not caught.
        :return: str
        """
        lines: list[str] = []

        if self.line > 0:
            lines.append(f"BOT syntax error at line {self.line}, column {self.column}:")
        else:
            lines.append("BOT syntax error:")

        if self.snippet != "":
            lines.append(f"    {self.snippet}")
            lines.append(f"    {' ' * max(self.column - 1, 0)}^")

        lines.append(f"    error: {self.message}")

        if self.token is not None:
            lines.append(f"    found: {self.token!r}")

        if self.hint is not None:
            lines.append(f"    hint: {self.hint}")

        return "\n".join(lines)

    def __str__(self) -> str:
        return self._render()


# CODE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SOURCE END -----
