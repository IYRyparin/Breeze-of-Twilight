import dataclasses


@dataclasses.dataclass(frozen=True)
class TypeExplainFormatter:
    DEFAULT_TYPE_EXPLAIN:       int = 0x00
    TABLE_TYPE_EXPLAIN:         int = 0x01
    LIST_TYPE_EXPLAIN:          int = 0x02
    ENUM_TYPE_EXPLAIN:          int = 0x03
    DATABASE_TYPE_EXPLAIN:      int = 0x04
    UNION_TYPE_EXPLAIN:         int = 0x05
    DEFAULT_CONVERSION_EXPLAIN: int = 0x10


@dataclasses.dataclass(frozen=True)
class ValueFormatter(object):
    DEFAULT_EMPTY_FORMATTER:          int = 0x00

    # CALL WITH INT OR FLOAT VALUE.
    DEFAULT_NUMBER_FORMATTER:         int = 0x10
    DEC_NUMBER_FORMATTER:             int = 0x11
    BIN_NUMBER_FORMATTER:             int = 0x12
    OCT_NUMBER_FORMATTER:             int = 0x13
    HEX_NUMBER_FORMATTER:             int = 0x14

    # CALL WITH STRING VALUE.
    DEFAULT_STRING_FORMATTER:         int = 0x20
    FILE_STRING_FORMATTER:            int = 0x21
    REGULAR_STRING_FORMATTER:         int = 0x22

    # CALL WITH THE LIST, TABLE, AND DATABASE.
    LIST_FORMATTER:                   int = 0x30
    TABLE_FORMATTER:                  int = 0x31
    DATABASE_FORMATTER:               int = 0x32

    # SPECIAL EXECUTION FORMATTER, CALL WITH SPECIAL VALUE.
    SEPARATOR:                        int = 0xD0
    DEFAULT_EMPTY_MUTABLE_FORMATTER:  int = 0xD1
    OPERATION_SIGNAL_FORMATTER:       int = 0xD2
    KEYWORD_SIGNAL_FORMATTER:         int = 0xD3
    KEYWORD_MUTABLE_SIGNAL_FORMATTER: int = 0xD4

    # CALL WITH CUSTOM VALUE, START WITH '0xE'.
    DEFAULT_CUSTOM_FORMATTER:         int = 0xE0
    PACKAGE_CUSTOM_FORMATTER:         int = 0xE1


@dataclasses.dataclass(frozen=True)
class ExtensionExplainFormatter(object):
    LIMIT_WITHIN_VALUE:                int = 0x00
    LIMIT_WITHOUT_VALUE:               int = 0x01

    LIMIT_WITHIN_STRING_REGULAR:       int = 0x02
    LIMIT_WITHOUT_STRING_REGULAR:      int = 0x03

    LIMIT_WITHIN_CONDITION_RULE:       int = 0x04
    LIMIT_WITHOUT_CONDITION_RULE:      int = 0x05

    LIMIT_WITHIN_CONDITION_AND_EQUAL:  int = 0x06
    LIMIT_WITHOUT_CONDITION_AND_EQUAL: int = 0x07
