import ctypes
import dataclasses


# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL DATACLASS. TO >>> ERROR CODE STRUCTURE.
#
# INTRODUCE SENTENCE.
# -> This file is used to define some global enumerate value signal to realize some part of exception.
# -> Why those need to be realized? Because the parser and executive will return some int value to indicate what happened in the process, and those int value will be defined in this file.
# -> Furthermore, the int value will be defined in a dataclass to make it more readable and maintainable.
#
# DATA SEGMENT START.

@dataclasses.dataclass(frozen=True)
class ErrorCodeFormatter:
    # +-------------------------------+----------------+--------------------------+--------------------------+
    # |             NAME              |     TYPE       |        VALUE             |         EXPLAIN          |
    # +-------------------------------+----------------+--------------------------+--------------------------+

    # ----- BASIC SUCCESS SIGNAL VALUE START -----
    # INTRODUCE SENTENCE.
    # -> From this part, it defines the success int value which will be returned in executive.
    # -> When parser parse file or executive the command successfully, it will return those signal and realize what should do next.
    #
    # SIGNAL SEGMENT START.

    DEFAULT_SUCCESS_SIGNAL:              ctypes.c_uint8 = ctypes.c_uint8(0x00)      # Default error code, will be used in other part.

    # SIGNAL SEGMENT END.
    # endregion
    #
    # SIGNAL SEGMENT END.
    #
    # ----- SEPARATING LINE -----
    #
    # ----- BASIC CRITICAL TERMINATE SIGNAL VALUE START -----
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From this part, it defines the critical terminate int signal which will be returned when some fatal error has been occurred.
    # -> When parser meet some part which get the critical parse failure that need to terminate to parse the file, it will be occurred.
    #
    # SIGNAL SEGMENT START.

    DEFAULT_CRITICAL_QUITTING_ERROR:     ctypes.c_uint8 = ctypes.c_uint8(0x10)

    DEFAULT_FILE_READ_ERROR:             ctypes.c_uint8 = ctypes.c_uint8(0x20)
    FILE_DECODE_ILLEGAL_SYNTAX:          ctypes.c_uint8 = ctypes.c_uint8(0x21)
    FILE_DECODE_ILLEGAL_FORMATTER:       ctypes.c_uint8 = ctypes.c_uint8(0x22)

    FILE_PERMISSION_DECLINED:            ctypes.c_uint8 = ctypes.c_uint8(0x2A)
    FILE_NOT_FOUND:                      ctypes.c_uint8 = ctypes.c_uint8(0x2B)

    # +-------------------------------+----------------+--------------------------+--------------------------+


@dataclasses.dataclass(frozen=True)
class TypeExplainFormatter:
    DEFAULT_TYPE_EXPLAIN: ctypes.c_uint8 = ctypes.c_uint8(0x00)
    LIST_TYPE_EXPLAIN:    ctypes.c_uint8 = ctypes.c_uint8(0x01)


@dataclasses.dataclass(frozen=True)
class ValueFormatter(object):
    DEFAULT_EMPTY_FORMATTER:          ctypes.c_uint8 = ctypes.c_uint8(0x00)
    DEFAULT_EMPTY_MUTABLE_FORMATTER:  ctypes.c_uint8 = ctypes.c_uint8(0x01)

    # CALL WITH INT OR FLOAT VALUE.
    DEFAULT_NUMBER_FORMATTER:         ctypes.c_uint8 = ctypes.c_uint8(0x10)
    DEC_NUMBER_FORMATTER:             ctypes.c_uint8 = ctypes.c_uint8(0x11)
    BIN_NUMBER_FORMATTER:             ctypes.c_uint8 = ctypes.c_uint8(0x12)
    OCT_NUMBER_FORMATTER:             ctypes.c_uint8 = ctypes.c_uint8(0x13)
    HEX_NUMBER_FORMATTER:             ctypes.c_uint8 = ctypes.c_uint8(0x14)

    # CALL WITH STRING VALUE.
    DEFAULT_STRING_FORMATTER:         ctypes.c_uint8 = ctypes.c_uint8(0x20)
    FILE_STRING_FORMATTER:            ctypes.c_uint8 = ctypes.c_uint8(0x21)
    REGULAR_STRING_FORMATTER:         ctypes.c_uint8 = ctypes.c_uint8(0x22)

    # LIMIT EXPLAIN INPUT VALUE.
    DEFAULT_LIMIT_LIST_EXPLAIN:  ctypes.c_uint8 = ctypes.c_uint8(0xD0)
    LIMIT_IN_RANGE_EXPLAIN:      ctypes.c_uint8 = ctypes.c_uint8(0xD1)
    LIMIT_NOT_IN_RANGE_EXPLAIN:  ctypes.c_uint8 = ctypes.c_uint8(0xD2)

    # CALL WITH CUSTOM VALUE, START WITH '0xE'.
    DEFAULT_CUSTOM_FORMATTER:    ctypes.c_uint8 = ctypes.c_uint8(0xE0)
    CUSTOM_CONVERSION_FORMATTER: ctypes.c_uint8 = ctypes.c_uint8(0xE1)


@dataclasses.dataclass(frozen=True)
class ExtensionExplainFormatter(object):
    LIMIT_WITHIN_VALUE:           ctypes.c_uint8 = ctypes.c_uint8(0x00)
    LIMIT_WITHOUT_VALUE:          ctypes.c_uint8 = ctypes.c_uint8(0x01)

    LIMIT_WITHIN_STRING_REGULAR:    ctypes.c_uint8 = ctypes.c_uint8(0x02)
    LIMIT_WITHOUT_STRING_REGULAR: ctypes.c_uint8 = ctypes.c_uint8(0x03)

    LIMIT_WITHIN_CONDITION_RULE:    ctypes.c_uint8 = ctypes.c_uint8(0x04)
    LIMIT_WITHOUT_CONDITION_RULE: ctypes.c_uint8 = ctypes.c_uint8(0x05)

    LIMIT_WITHIN_CONDITION_AND_EQUAL: ctypes.c_uint8 = ctypes.c_uint8(0x06)
    LIMIT_WITHOUT_CONDITION_AND_EQUAL: ctypes.c_uint8 = ctypes.c_uint8(0x07)


# DATA SEGMENT END.
# endregion
#
# IDENTIFICATION END.
#
# ----- SOURCE END -----
