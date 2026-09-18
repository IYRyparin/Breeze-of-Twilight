from typing import Final, NoReturn, Optional

from src.parsecheck.syntax.errors import BOTSyntaxError
from src.parsecheck.syntax.tokens import Token, TokenType, tokenize


# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> BOT GRAMMAR TABLE.
#
# INTRODUCE SENTENCE.
# -> The tables below are the whole BOT grammar in a single glance. They mirror grammar/Grammar.bnf
#    but are corrected against what grammar/example.bot and grammar/basic.bot actually write:
#      * every LIMIT / REGULAR carries parentheses (the parser requires them too),
#      * COMPARE rules use "-> RETURN" even though the BNF forgot the arrow,
#      * a data declaration *must* carry its "[Type]" because the parser silently drops every
#        declaration that does not (see ConfigurationStandalone._data_load_databases).
#
# GLOBAL VALUE SEGMENT START.

RESERVED_NAMES: Final[frozenset[str]] = frozenset({
    "identification", "databases-start", "databases-end",
    "conversion-start", "conversion-end", "conversion", "compare",
})

TYPE_KEYWORD_ALIAS: Final[dict[str, str]] = {
    "str": "string",
    "dbl": "float",
    "flt": "float",
}

# Types that never take a "<...>" parameter list.
PLAIN_TYPE_KEYWORD: Final[frozenset[str]] = frozenset({
    "int", "string", "bool", "float", "file", "anything",
})

ACCESS_MODIFIER_KEYWORD:  Final[frozenset[str]] = frozenset({"cst", "mut"})
BOOLEAN_KEYWORD:          Final[frozenset[str]] = frozenset({"true", "false"})
NULL_KEYWORD:             Final[frozenset[str]] = frozenset({"null"})

IDENTIFICATION_FIELD_VALUE: Final[dict[str, str]] = {
    "configuration-id":       "string",
    "configuration-version":  "number",
    "configuration-encode":   "string",
    "configuration-readonly": "boolean",
}

WITH_KEYWORD: Final[frozenset[str]] = frozenset({
    "with-time", "with-machine", "with-path", "with-locale",
    "with-language", "with-network", "with-count", "with-value",
})

# WITH-VALUE is the only one that may bring its own default value: "... other_val [STR] = CALL ...()".
WITH_KEYWORD_ALLOWING_VALUE: Final[frozenset[str]] = frozenset({"with-value"})

EXTENSION_KEYWORD: Final[frozenset[str]] = frozenset({"limit", "regular"})

RELATIONAL_OPERATOR: Final[frozenset[str]] = frozenset({"<", "<=", "==", ">=", ">", "!="})
ADDITIVE_OPERATOR:   Final[frozenset[str]] = frozenset({"+", "-"})
MULTIPLICATIVE_OPERATOR: Final[frozenset[str]] = frozenset({"*", "/", "//", "%", "**", "&", "|", "^", "<<", ">>"})


# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION CLASS PART. TO >>> SYNTAX VALIDATOR.
#
# INTRODUCE SENTENCE.
# -> A recursive descent validator: it walks the token stream produced by the lexer and raises
#    BOTSyntaxError the moment something does not fit the grammar. It deliberately builds nothing -
#    no AST, no data - because the parser already owns that job. Its only task is to decide
#    "is this file well formed?" before the parser touches a single character of it.
#
# CODE SEGMENT START.


class SyntaxValidator(object):
    def __init__(self, source: str) -> None:
        self._source: str = source
        self._tokens: list[Token] = tokenize(source)
        self._index: int = 0

    # ----- TOKEN STREAM ACCESS -----
    # region

    @property
    def _token(self) -> Token:
        """:return: Token   The token under the cursor."""
        return self._tokens[min(self._index, len(self._tokens) - 1)]

    def _peek(self, ahead: int = 0) -> Token:
        """:return: Token   Look ahead; never runs past the end of the stream."""
        return self._tokens[min(self._index + ahead, len(self._tokens) - 1)]

    def _advance(self) -> Token:
        """:return: Token   Consume and return the current token."""
        token: Token = self._tokens[min(self._index, len(self._tokens) - 1)]
        self._index = min(self._index + 1, len(self._tokens) - 1)
        return token

    def _error(self, message: str, token: Optional[Token] = None, hint: Optional[str] = None) -> NoReturn:
        report_token: Token = token if token is not None else self._token
        raise BOTSyntaxError(
            message,
            offset=report_token.offset,
            source=self._source,
            hint=hint,
            token=report_token.describe(),
        )

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- EXPECTATION HELPERS -----
    # region

    def _expect_operator(self, operator: str, hint: Optional[str] = None) -> Token:
        if not self._token.is_operator(operator):
            self._error(f"Expected '{operator}' here.", hint=hint)
        return self._advance()

    def _expect_word(self, *words: str, hint: Optional[str] = None) -> Token:
        if not self._token.is_word(*words):
            expected: str = " or ".join(f"'{word.upper()}'" for word in words)
            self._error(f"Expected {expected} here.", hint=hint)
        return self._advance()

    def _expect_name(self, what: str) -> Token:
        """
        Consume an identifier that is used as a *name* (data key, conversion name, member name).
        """
        token: Token = self._token

        if token.kind != TokenType.IDENT:
            self._error(f"Expected a {what} name here, such as 'EXAMPLE_VALUE'.")

        if token.word in RESERVED_NAMES:
            self._error(
                f"Reserved keyword {token.raw!r} cannot be used as a {what} name.",
                token=token,
                hint="Choose another name for this key.",
            )

        return self._advance()

    def _expect_close_angle(self, hint: Optional[str] = None) -> None:
        """
        Consume the '>' closing a "<...>" parameter list.

        The lexer emits '>>' as one shift operator, so a nested type such as TABLE<TABLE<INT>>
        arrives as a single '>>' token and has to give one of its characters back.
        """
        token: Token = self._token

        if token.is_operator(">"):
            self._advance()
            return

        if token.is_operator(">>"):
            self._tokens[self._index] = Token(TokenType.OP, ">", token.offset + 1, ">")
            return

        self._error("Expected '>' to close the type parameter list.", hint=hint)

    def _expect_statement_end(self, closing: str = "}") -> None:
        """
        Consume the ';' closing a statement.

        The very last statement of a block is allowed to omit it (grammar/example.bot does exactly
        that for CONVERSION Outer), everywhere else it is mandatory.
        """
        if self._token.is_operator(";"):
            self._advance()
            return

        if self._token.is_operator(closing):
            return

        self._error(
            "Expected ';' to close this statement.",
            hint=f"A statement inside a block has to end with ';' before '{closing}'.",
        )

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- SCOPE DUPLICATE TRACKING -----
    # region

    def _declare_name(self, token: Token, scope: dict[str, str], what: str) -> None:
        name: str = token.word

        if name in scope:
            previous_line: int = BOTSyntaxError("", offset=int(scope[name]), source=self._source).line
            self._error(
                f"Duplicated {what} name {token.raw!r}, it was already declared on line {previous_line}.",
                token=token,
                hint="The parser keeps only the first declaration, so the second one is silently lost.",
            )

        scope[name] = str(token.offset)

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- TOP LEVEL PROGRAM -----
    # region

    def validate(self) -> None:
        """
        Entry point: validate a whole configuration file.
        :return: None
        """
        self._parse_program()

    def _parse_program(self) -> None:
        seen_identification: set[str] = set()

        # Everything in front of DATABASES-START must be an IDENTIFICATION statement.
        while True:
            token: Token = self._token

            if token.kind == TokenType.EOF:
                self._error(
                    "Missing databases part: the file ends before the DATABASES-START division.",
                    hint='Every configuration needs a "DATABASES-START;" block.',
                )

            if token.is_word("databases-start"):
                break

            if token.is_word("conversion-start"):
                self._error(
                    "Missing databases part: found CONVERSION-START before DATABASES-START.",
                    token=token,
                    hint="The databases block always comes first.",
                )

            self._parse_identification_statement(seen_identification)

        self._parse_databases_part()

        if self._token.is_word("conversion-start"):
            self._parse_conversion_part()

        if self._token.kind != TokenType.EOF:
            self._error(
                "Unexpected trailing content after the last division.",
                hint="The file has to end with the CONVERSION-END (or DATABASES-END) line.",
            )

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- IDENTIFICATION PART -----
    # region

    def _parse_identification_statement(self, seen: set[str]) -> None:
        head: Token = self._token

        if not head.is_word("identification"):
            self._error(
                "Expected an IDENTIFICATION statement or the DATABASES-START division.",
                token=head,
                hint="Identification lines look like: IDENTIFICATION CONFIGURATION-ID \"my-config\";",
            )

        self._advance()

        field: Token = self._token
        if field.kind != TokenType.IDENT or field.word not in IDENTIFICATION_FIELD_VALUE:
            self._error(
                f"Unknown identification field {field.raw!r}.",
                token=field,
                hint="Supported fields are CONFIGURATION-ID, CONFIGURATION-VERSION, "
                     "CONFIGURATION-ENCODE and CONFIGURATION-READONLY.",
            )

        self._advance()

        if field.word in seen:
            self._error(
                f"Duplicated IDENTIFICATION {field.raw.upper()} declaration.",
                token=field,
                hint="Each identification field may be declared only once.",
            )
        seen.add(field.word)

        expectation: str = IDENTIFICATION_FIELD_VALUE[field.word]
        value: Token = self._token

        if expectation == "string":
            if value.kind != TokenType.STRING:
                self._error(
                    f"{field.raw.upper()} expects a quoted string value.",
                    token=value,
                    hint='Write the value inside double quotes, e.g. "UTF-8".',
                )
            self._advance()

        elif expectation == "number":
            if value.kind != TokenType.NUMBER:
                self._error(
                    f"{field.raw.upper()} expects a numeric value.",
                    token=value,
                    hint="Write a plain number, e.g. 1.0.",
                )
            self._advance()

        else:  # boolean
            if not (value.is_word(*BOOLEAN_KEYWORD) or value.kind == TokenType.NUMBER):
                self._error(
                    f"{field.raw.upper()} expects a boolean value.",
                    token=value,
                    hint="Use TRUE or FALSE.",
                )
            self._advance()

        self._expect_operator(";", hint="Every IDENTIFICATION statement ends with ';'.")

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- DATABASES PART -----
    # region

    def _parse_databases_part(self) -> None:
        self._expect_word("databases-start")
        self._expect_operator(";")

        start_token: Token = self._expect_operator(
            "{", hint="The databases block has to open with '{' right after DATABASES-START;")

        self._parse_database_block(start_token, root=True)

        self._expect_operator(";", hint="The databases block closes with '};' on its own line.")
        self._expect_word("databases-end")
        self._expect_operator(";")

    def _parse_database_block(self, opener: Token, root: bool = False) -> None:
        """
        Validate one '{ ... }' group of data declarations.

        :param opener: Token   The '{' that opened this block, used for the "where does it end" error.
        :param root:   bool    True for the block owned by DATABASES-START.
        :return: None
        """
        scope: dict[str, str] = {}

        while not self._token.is_operator("}"):
            if self._token.kind == TokenType.EOF:
                self._error(
                    "Unterminated databases block, reached the end of the file while looking for '}'.",
                    token=opener,
                    hint="Every '{' opened inside DATABASES-START has to be closed by '}'.",
                )

            checkpoint: int = self._index
            self._parse_data_declaration(scope)

            if self._index == checkpoint:
                self._error("Cannot move past this token while reading a data declaration.")

        self._advance()  # Drop the closing '}'.

    def _parse_data_declaration(self, scope: dict[str, str]) -> None:
        name: Token = self._expect_name("data")
        self._declare_name(name, scope, "data")

        # A type is mandatory here: the parser quietly skips any declaration without one, so
        # accepting it here would mean accepting silently lost configuration.
        if not self._token.is_operator("["):
            self._error(
                f"Missing the type declaration of {name.raw!r}.",
                hint="Write the type inside brackets, e.g. [INT], [STR] or [TABLE<INT, STR>].",
            )

        self._advance()
        self._parse_type_specification()
        self._expect_operator("]", hint="The type declaration has to be closed by ']'.")

        if self._token.is_word(*ACCESS_MODIFIER_KEYWORD):
            previous: Token = self._advance()

            if self._token.is_word(*ACCESS_MODIFIER_KEYWORD):
                self._error(
                    f"Access modifier given twice ({previous.raw!r} and {self._token.raw!r}).",
                    hint="A value is either CST or MUT, never both.",
                )

        self._expect_operator("=", hint="A declaration looks like NAME [TYPE] CST = value;")

        self._parse_value_or_body(scope)

        # Optional extension rules: "-> LIMIT(...), REGULAR(...)".
        while self._token.is_operator(",") or self._token.is_operator("->"):
            self._advance()
            self._parse_extension_item()

        self._expect_statement_end()

    def _parse_value_or_body(self, scope: dict[str, str]) -> None:
        token: Token = self._token

        if token.is_word(*NULL_KEYWORD):
            self._advance()
            return

        if token.is_operator("{"):
            self._advance()
            self._parse_database_block(token)
            return

        if token.is_operator("["):
            self._parse_table_literal()
            return

        self._parse_expression()

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- TYPE SPECIFICATION -----
    # region

    def _parse_type_specification(self) -> None:
        token: Token = self._token

        if token.kind != TokenType.IDENT:
            self._error(
                "Expected a type name inside the brackets.",
                hint="Supported types are INT, STR, BOOL, FLOAT, FILE, ANYTHING, "
                     "DATABASE, ENUM<...>, TABLE<...>, UNION<...> and CONVERSION<...>.",
            )

        name: str = token.word
        self._advance()

        canonical: str = TYPE_KEYWORD_ALIAS.get(name, name)

        if canonical in PLAIN_TYPE_KEYWORD:
            if self._token.is_operator("<"):
                self._error(
                    f"Type {token.raw.upper()} does not take any parameter.",
                    hint="Remove the '<...>' part.",
                )
            return

        if canonical == "database":
            # DATABASE is the only optional parameter form: [DATABASE] and [DATABASE<INT>] both work.
            if self._token.is_operator("<"):
                self._advance()
                self._parse_type_specification()
                self._expect_close_angle()
            return

        if canonical in ("table", "union"):
            self._expect_open_angle(token)
            column_name: str = "column" if canonical == "table" else "member"

            self._parse_type_specification()
            while self._token.is_operator(","):
                self._advance()
                self._parse_type_specification()
            self._expect_close_angle(hint=f"A {canonical.upper()} needs at least one {column_name} type.")
            return

        if canonical == "conversion":
            self._expect_open_angle(token)
            self._parse_type_specification()
            self._expect_close_angle(hint="CONVERSION needs exactly one result type, e.g. CONVERSION<INT>.")
            return

        if canonical == "enum":
            self._expect_open_angle(token)
            self._parse_enum_member_list()
            self._expect_close_angle(hint="An ENUM needs at least one candidate value, e.g. ENUM<1, 2, 3>.")
            return

        self._error(
            f"Unsupported configuration data type: {token.raw!r}",
            token=token,
            hint="Supported types are INT, STR, BOOL, FLOAT, FILE, ANYTHING, "
                 "DATABASE, ENUM<...>, TABLE<...>, UNION<...> and CONVERSION<...>.",
        )

    def _expect_open_angle(self, owner: Token) -> None:
        if not self._token.is_operator("<"):
            self._error(
                f"Type {owner.raw.upper()} requires a '<...>' parameter list.",
                hint=f"Write something like {owner.raw.upper()}<INT>.",
            )
        self._advance()

    def _parse_enum_member_list(self) -> None:
        """
        Validate the candidate list of an ENUM.

        Every member has to be a literal (number, string or boolean) and all of them have to be of
        the same kind, because LIMIT compares them with '==' against the stored value.
        """
        member_kind: Optional[str] = None

        def _parse_member() -> None:
            nonlocal member_kind

            token: Token = self._token

            if token.kind in (TokenType.NUMBER, TokenType.STRING, TokenType.CHAR):
                self._advance()
                kind: str = token.kind
            elif token.is_word(*BOOLEAN_KEYWORD):
                self._advance()
                kind = "boolean"
            else:
                self._error(
                    "Expected a constant value inside the ENUM list.",
                    token=token,
                    hint="An ENUM member is a number, a quoted string or TRUE/FALSE, never an expression.",
                )

            if member_kind is None:
                member_kind = kind
            elif member_kind != kind:
                self._error(
                    f"Mixed ENUM member types, expected another {member_kind} value.",
                    token=token,
                    hint="All candidates of one ENUM must be of the same kind.",
                )

        _parse_member()
        while self._token.is_operator(","):
            self._advance()
            _parse_member()

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- TABLE LITERAL -----
    # region

    def _parse_table_literal(self) -> None:
        opener: Token = self._expect_operator("[")

        if self._token.is_operator("]"):
            self._advance()
            return

        while not self._token.is_operator("]"):
            if self._token.kind == TokenType.EOF:
                self._error(
                    "Unterminated table literal, reached the end of the file while looking for ']'.",
                    token=opener,
                )

            checkpoint: int = self._index

            if self._token.is_operator("("):
                self._advance()

                if self._token.is_operator(")"):
                    self._error("Empty table row, a row needs at least one value.")

                self._parse_expression()
                while self._token.is_operator(","):
                    self._advance()
                    self._parse_expression()

                self._expect_operator(")", hint="A table row looks like (1, \"Bob\", TRUE),")
            else:
                # A flat row without parentheses, e.g. [1, 2, 3].
                self._parse_expression()

            if self._index == checkpoint:
                self._error("Cannot move past this token while reading a table row.")

            if self._token.is_operator(","):
                self._advance()  # A trailing comma in front of ']' is allowed.
                continue

            break

        self._expect_operator("]", hint="A table literal has to be closed by ']'.")

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- EXTENSION RULES (LIMIT / REGULAR) -----
    # region

    def _parse_extension_item(self) -> None:
        token: Token = self._token

        if token.kind != TokenType.IDENT or token.word not in EXTENSION_KEYWORD:
            self._error(
                f"Expected LIMIT or REGULAR after '->', found {token.describe()}.",
                token=token,
                hint="An extension rule looks like: -> LIMIT(1, 2, 5 TO 10)",
            )

        self._advance()

        if not self._token.is_operator("("):
            self._error(
                f"{token.raw.upper()} requires a parenthesised argument list.",
                hint=f"Write {token.raw.upper()}(...) instead of {token.raw.upper()} ...",
            )
        self._advance()

        if self._token.is_operator(")"):
            self._error(
                f"Empty {token.raw.upper()} argument list.",
                hint=f"{token.raw.upper()} needs at least one value, e.g. {token.raw.upper()}(1, 2, 3).",
            )

        self._parse_extension_argument()
        while self._token.is_operator(","):
            self._advance()
            self._parse_extension_argument()

        self._expect_operator(")", hint=f"Close the {token.raw.upper()} argument list with ')'.")

    def _parse_extension_argument(self) -> None:
        """
        One argument of LIMIT / REGULAR:

            EXCLUDE SUM 1 TO 3     -> drop every value in 1..3
            10 TO 20               -> inclusive range
            "^ACPacp$"             -> plain value (or a regex for REGULAR)
        """
        if self._token.is_word("exclude"):
            self._advance()

        self._parse_expression()

        if self._token.is_word("to"):
            self._advance()
            self._parse_expression()

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- EXPRESSION PART -----
    # region

    def _parse_expression(self) -> None:
        self._parse_relational()

    def _parse_relational(self) -> None:
        self._parse_additive()

        while self._token.kind == TokenType.OP and self._token.value in RELATIONAL_OPERATOR:
            self._advance()
            self._parse_additive()

    def _parse_additive(self) -> None:
        self._parse_multiplicative()

        while self._token.kind == TokenType.OP and self._token.value in ADDITIVE_OPERATOR:
            self._advance()
            self._parse_multiplicative()

    def _parse_multiplicative(self) -> None:
        self._parse_prefix()

        while self._token.kind == TokenType.OP and self._token.value in MULTIPLICATIVE_OPERATOR:
            self._advance()
            self._parse_prefix()

    def _parse_prefix(self) -> None:
        token: Token = self._token

        if token.is_word("return"):
            self._advance()
            self._parse_prefix()
            return

        if token.is_word("call"):
            self._advance()
            self._parse_call_target()
            return

        if token.is_word("format"):
            self._advance()
            self._expect_word(
                "default",
                hint="FORMAT is a placeholder and always carries a fallback, e.g. FORMAT DEFAULT \"1\".",
            )
            self._parse_prefix()
            return

        if token.is_word("default"):
            self._advance()
            self._parse_prefix()
            return

        if token.is_word("sum"):
            self._advance()
            self._parse_expression()
            self._expect_word("to", hint="SUM needs a range, e.g. SUM 1 TO 3.")
            self._parse_expression()
            return

        self._parse_atom()

    def _parse_call_target(self) -> None:
        """
        Validate what follows CALL: a (possibly dotted) name with optional arguments,
        such as package.GetCurrentTime() or CountDown.
        """
        self._expect_name("callable")

        while self._token.is_operator("."):
            self._advance()
            self._expect_name("member")

        if self._token.is_operator("("):
            self._advance()

            if not self._token.is_operator(")"):
                self._parse_expression()
                while self._token.is_operator(","):
                    self._advance()
                    self._parse_expression()

            self._expect_operator(")", hint="Close the call argument list with ')'.")

    def _parse_atom(self) -> None:
        token: Token = self._token

        if token.kind in (TokenType.NUMBER, TokenType.STRING, TokenType.CHAR):
            self._advance()
            return

        if token.is_word(*BOOLEAN_KEYWORD) or token.is_word(*NULL_KEYWORD):
            self._advance()
            return

        if token.is_operator("("):
            self._advance()
            self._parse_expression()
            self._expect_operator(")", hint="Close the sub-expression with ')'.")
            self._parse_postfix()
            return

        if token.kind == TokenType.IDENT:
            self._advance()
            self._parse_postfix()
            return

        self._error(
            f"Expected a value here, found {token.describe()}.",
            hint="A value is a number, a string, TRUE/FALSE, NULL, a name or a CALL expression.",
        )

    def _parse_postfix(self) -> None:
        """
        Validate the trailing part of a member access: ".name", "(arguments)" and "[index]" /
        "[start TO end]" the way the conversion rules use them (other_val[0], other_val[1 TO 4]).
        """
        while True:
            if self._token.is_operator("."):
                self._advance()
                self._expect_name("member")
                continue

            if self._token.is_operator("("):
                self._advance()

                if not self._token.is_operator(")"):
                    self._parse_expression()
                    while self._token.is_operator(","):
                        self._advance()
                        self._parse_expression()

                self._expect_operator(")", hint="Close the argument list with ')'.")
                continue

            if self._token.is_operator("["):
                self._advance()

                self._parse_expression()
                if self._token.is_word("to"):
                    self._advance()
                    self._parse_expression()

                self._expect_operator("]", hint="Close the index with ']'.")
                continue

            return

    # endregion
    # ----- SEPARATING LINE -----
    #
    # ----- CONVERSION PART -----
    # region

    def _parse_conversion_part(self) -> None:
        self._expect_word("conversion-start")
        self._expect_operator(";")
        opener: Token = self._expect_operator("{", hint="The conversion part opens with '{'.")

        scope: dict[str, str] = {}

        while not self._token.is_operator("}"):
            if self._token.kind == TokenType.EOF:
                self._error(
                    "Unterminated conversion part, reached the end of the file while looking for '}'.",
                    token=opener,
                )

            checkpoint: int = self._index
            self._parse_conversion_declaration(scope)

            if self._index == checkpoint:
                self._error("Cannot move past this token while reading a conversion declaration.")

        self._advance()

        self._expect_operator(";", hint="The conversion part closes with '};' on its own line.")
        self._expect_word("conversion-end")
        self._expect_operator(";")

    def _parse_conversion_declaration(self, scope: dict[str, str]) -> None:
        self._expect_word("conversion")

        name: Token = self._expect_name("conversion")
        self._declare_name(name, scope, "conversion")

        if self._token.is_operator("["):
            self._advance()
            self._parse_type_specification()
            self._expect_operator("]", hint="Close the conversion result type with ']'.")

        self._parse_with_specification()

        if self._token.is_word("limit"):
            self._advance()
            self._parse_expression()
            self._expect_word("to", hint="A conversion limit is a range, e.g. LIMIT 1 TO 50.")
            self._parse_expression()

        opener: Token = self._token
        if not opener.is_operator("{"):
            self._error(
                "Expected the '{' opening the conversion rule body.",
                hint="A CONVERSION always ends with a '{ ... }' block holding its COMPARE rules.",
            )
        self._advance()

        while not self._token.is_operator("}"):
            if self._token.kind == TokenType.EOF:
                self._error(
                    "Unterminated conversion body, reached the end of the file while looking for '}'.",
                    token=opener,
                )

            checkpoint: int = self._index
            self._parse_compare_rule()

            if self._index == checkpoint:
                self._error("Cannot move past this token while reading a COMPARE rule.")

        self._advance()
        self._expect_statement_end("}")

    def _parse_with_specification(self) -> None:
        token: Token = self._token

        if token.kind != TokenType.IDENT or token.word not in WITH_KEYWORD:
            self._error(
                f"Expected a WITH-* conversion source, found {token.describe()}.",
                token=token,
                hint="Supported sources are WITH-TIME, WITH-PATH, WITH-VALUE, WITH-COUNT, "
                     "WITH-MACHINE, WITH-LOCALE, WITH-LANGUAGE and WITH-NETWORK.",
            )

        self._advance()
        self._expect_name("conversion source")

        if self._token.is_operator("["):
            self._advance()
            self._parse_type_specification()
            self._expect_operator("]", hint="Close the conversion source type with ']'.")

        if token.word in WITH_KEYWORD_ALLOWING_VALUE and self._token.is_operator("="):
            self._advance()
            self._parse_expression()

    def _parse_compare_rule(self) -> None:
        self._expect_word("compare")

        if self._token.is_word("default"):
            self._advance()
        else:
            self._parse_expression()

        # grammar/Grammar.bnf forgot it, but every real rule writes "-> RETURN". Both are accepted.
        if self._token.is_operator("->"):
            self._advance()

        self._expect_word("return", hint="A COMPARE rule returns a value, e.g. COMPARE DEFAULT -> RETURN 1;")

        self._parse_expression()
        self._expect_statement_end("}")

    # endregion
    # ----- SEPARATING LINE -----


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION FUNCTION PART. TO >>> PUBLIC ENTRY.
#
# CODE SEGMENT START.


def validate_syntax(source: str) -> None:
    """
    Run the whole syntax validation over a configuration source.

    Nothing is returned: a correct file simply falls through, anything else raises BOTSyntaxError
    with the exact line and column of the mistake, which stops the parser before it starts.

    :param source: str   Untouched configuration source.
    :return: None
    """
    SyntaxValidator(source).validate()


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
