# VALUE SAVING STRUCTURE

import ctypes
import re
from decimal import Decimal
from typing import Any

from src.parseutil.kword import CALCULATE_CHAR
from src.parseutil.signal import ValueFormatter, ExtensionExplainFormatter, TypeExplainFormatter
from src.parsefunc.function import isinstance_loose, ConversionDecimal
from src.parseutil.column import evaluate_stack


# ----- SOURCE START -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> LANGUAGE PARSER.
#
# region
# INTRODUCE SENTENCE.
# -> This file defines the critical function which will be used to parse the BOT file.
# -> From here, it can parse BOT configuration's data and grammar tree to realize configuration's parse.
# -> Furthermore, because this language's function has multiple type which python may not support...
# -> ...so I need to use some special part to do it.
# -> So...I build a middle part from Python and Breeze of Twilight,
# -> it can get the executive code from Python and call target part of BOT.
#
# CODE SEGMENT START.

# ----- CONFIGURATION STANDALONE -----
#
# region
# INTRODUCE SENTENCE.
# -> This class is used to build a standalone configuration data.
# -> Because the configuration file has some special part which may not be supported by dict,
# -> so I build a custom class to save the data, and I can use this class to parse the data and build grammar tree.
# -> Afterwords, I will build a configuration manager to manage the configuration file.
# -> Because when you have countless configuration files, it may be hard to manage and call them manual,
# -> so I need to build a manager to realize it.
# -> So from that, I need to build a configuration standalone and manager to realize it.
#
# DATA SEGMENT START.


class ConfigurationDataStandaloneSegmentStructure(object):
    def __init__(self) -> None:
        """
        Warning: There haven't check the value's type! Be careful!
        """
        # +----------------------+----------------------------------+---------------------------+-----------------------------------+
        # |        NAME          |               TYPE               |          VALUE            |             EXPLAIN               |
        # +----------------------+----------------------------------+---------------------------+-----------------------------------+
        self._name:               str                               = ""                          # Name of the element.
        self._probable_type:      tuple[list[type], ctypes.c_uint8] = ([], ctypes.c_uint8(0x00))  # What type it can be used.
        self._value:              list[tuple[Any, ctypes.c_uint8]]  = []                          # Final value of the element.
        self._format:             ctypes.c_uint8                    = ctypes.c_uint8(0x00)        # Value and segment's format of the element.
        self._changeable:         bool                              = True                        # A signal, used to means that this value can be changed or not.
        self._limit_value_list:   list[tuple[Any, ctypes.c_uint8]]  = []                          # Which value you want to reject or accept.
        # +----------------------+----------------------------------+---------------------------+-----------------------------------+

    # IDENTIFICATION SEGMENT PART. TO >>> BASIC VALUE SETTER SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, is the function's setter which used to check the value's status.
    # -> To keep
    # ->
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def _row_of(row_item: Any) -> list[Any]:
        """A single column row may be stored bare; always hand it back as a column list."""
        return row_item if isinstance_loose(row_item, list) else [row_item]

    @classmethod
    def _match_row(cls, row_values: list[Any], column_types: list) -> bool:
        """
        Check one table row against the declared column signature.

        A column entry that is itself a list marks a nested table, so it recurses.

        :param row_values: list[Any]    The row content.
        :param column_types: list       Column signature, see `table_segment_type_checker`.
        :return: bool
        """
        if len(row_values) != len(column_types):
            return False

        for value_item, column_type in zip(row_values, column_types):
            if isinstance(column_type, list):  # Nested table column.
                if not isinstance_loose(value_item, list):
                    return False
                if not all(cls._match_row(cls._row_of(nested_item), column_type) for nested_item in value_item):
                    return False
                continue

            if not isinstance_loose(value_item, column_type):
                return False

        return True

    def _check_in_type(self, value: Any) -> bool:
        """
        This function is used to check the value's type is in the probable type list or not.
        When not in the probable type list, it will return False.
        :param value: Any   Explain method information.
        :return: bool
        """
        match self._probable_type[1]:
            case TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN:  # Check with default type explain checker mode.
                for probably_type_item in self._probable_type[0]:
                    if isinstance_loose(value, probably_type_item):
                        return True

                # Or anything else, so we can return the false.
                return False

            # Check with list explain checker mode.
            case TypeExplainFormatter.LIST_TYPE_EXPLAIN:
                # A table stores one row per entry and every row has to follow the declared
                # column signature. The old code indexed the type container itself (that is the
                # whole signature list) instead of its per-column entries, so every table check
                # either blew up with IndexError or silently answered False.
                if not isinstance_loose(value, list):
                    return False

                return all(self._match_row(self._row_of(row_item), self._probable_type[0]) for row_item in value)

            # Make sure don't throw error.
            case _:
                return False

    @staticmethod
    def _check_in_limit(value: Any, limit_element: tuple[Any, ctypes.c_uint8]) -> bool:
        """

        :param value: Any   Target checked value.
        :param limit_element: tuple[Any, ctypes.c_uint8]   Limit information.
        :return: bool
        """
        match limit_element[1]:  # Limit with in value, just compare it and return it is equal or not.
            case ExtensionExplainFormatter.LIMIT_WITHIN_VALUE:              return value == limit_element[0]                                   # noqa
            case ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE:             return value != limit_element[0]                                   # noqa

            # Limit with string regular, on here it will change it into the string, and try to match it is in the rule or not.
            case ExtensionExplainFormatter.LIMIT_WITHIN_STRING_REGULAR:      return re.search(limit_element[0], str(value)) is not None        # noqa
            case ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR:     return re.search(limit_element[0], str(value)) is None            # noqa

            # Limit with condition rule, welp...just means this is the left limit or the right limit.
            # The tuple is always (low, high): the old code read [1] and [2] on the negated
            # branches, which silently compared the wrong pair of a three slot tuple.
            case ExtensionExplainFormatter.LIMIT_WITHIN_CONDITION_RULE:       return limit_element[0][0] < value < limit_element[0][1]         # noqa
            case ExtensionExplainFormatter.LIMIT_WITHOUT_CONDITION_RULE:      return not limit_element[0][0] < value < limit_element[0][1]     # noqa

            # Just with in the equal.
            case ExtensionExplainFormatter.LIMIT_WITHIN_CONDITION_AND_EQUAL:  return limit_element[0][0] <= value <= limit_element[0][1]       # noqa
            case ExtensionExplainFormatter.LIMIT_WITHOUT_CONDITION_AND_EQUAL: return not limit_element[0][0] <= value <= limit_element[0][1]   # noqa

            # Welp...So has this line of code can be occurred?
            case _:
                return False

    @staticmethod
    def _calculate(value: list[tuple[Any, ctypes.c_uint8]]) -> Any:
        return evaluate_stack(value)

    def format(self, *args) -> None:
        argument = iter(args)
        try:
            for index, value in enumerate(self._value):
                if value[1] == ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER:
                    self._value[index] = (next(argument), ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER)
        except StopIteration:
            pass

    # CODE SEGMENT PART END.
    # endregion

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def changeable(self) -> bool:
        return self._changeable

    @changeable.setter
    def changeable(self, new_changeable: bool) -> None:
        self._changeable = new_changeable

    @property
    def value(self) -> Any:
        # A table keeps one entry per row, so reducing the stack would throw every row but the
        # first one away: every row is handed back on its own instead.
        if self._probable_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
            return [self._table_row(item[0]) for item in self._value]

        push_value: Any = evaluate_stack(self._value)

        # FLOAT arithmetic is done with Decimal to keep the precision, but the declared type is
        # float, so the caller must receive a float.
        if isinstance(push_value, (ConversionDecimal, Decimal)):
            return float(push_value)

        return push_value

    @staticmethod
    def _table_row(row_item: Any) -> Any:
        """One table row; a single column table hands back the bare value instead of a 1-tuple."""
        if isinstance(row_item, ConfigurationDataStandaloneSegmentStructure):
            row_item = row_item.value
        if isinstance_loose(row_item, list) and len(row_item) == 1 and not isinstance_loose(row_item[0], list):
            return row_item[0]
        return row_item

    @value.setter
    def value(self, new_value: Any) -> None:
        if not self._changeable:  # Check the changeable.
            raise InterruptedError("This is a read-only value.")

        # Accept both the internal stack form and a plain python value, so callers can simply
        # write `node.value = 5` without knowing anything about the value formatters.
        value_stack: list[tuple[Any, ctypes.c_uint8]] = self._as_value_stack(new_value)

        # Check the type and limit, make sure it's valid.
        if self._probable_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
            rows: list[Any] = [item[0] for item in value_stack]
            if not self._check_in_type(rows):
                raise TypeError("Error type of the value in here.")
            self._check_limit_rows(rows)

        else:
            calc: Any = evaluate_stack(value_stack)
            if not self._check_in_type(calc):
                raise TypeError("Error type of the value in here.")
            self._check_limits(calc)

        # Or nothing limit in here, so we can just add it into the value part.
        self._value = value_stack

    @staticmethod
    def _as_value_stack(new_value: Any) -> list[tuple[Any, ctypes.c_uint8]]:
        """
        Normalise anything the caller assigns into the internal `list[tuple[Any, formatter]]`
        representation.

        :param new_value: Any
        :return: list[tuple[Any, ctypes.c_uint8]]
        """
        looks_internal: bool = (
            isinstance_loose(new_value, list)
            and len(new_value) > 0
            and isinstance(new_value[0], tuple)
            and len(new_value[0]) == 2
        )
        if looks_internal:
            return list(new_value)

        if isinstance_loose(new_value, list):
            return [(item, ValueFormatter.DEFAULT_EMPTY_FORMATTER) for item in new_value]

        return [(new_value, ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

    def _check_limits(self, calc: Any) -> None:
        """
        Raise when a value breaks its LIMIT / REGULAR rules.

        The list is a DISJUNCTION: one accepting rule is enough, which is what makes
        `LIMIT(1, 2, 5, 10)` mean "any of these" and `LIMIT(EXCLUDE 5)` mean "anything but 5",
        and what lets both kinds be mixed in a single list.

        :param calc: Any    Already reduced value.
        :return: None
        """
        if len(self._limit_value_list) == 0:
            return

        for limit_item in self._limit_value_list:
            if self._check_in_limit(calc, limit_item):
                return

        raise ValueError("This value is in the limit list's rule, please check and change the rule.")

    def _check_limit_rows(self, rows: list[Any]) -> None:
        """Same check as `_check_limits` but applied to every row of a table."""
        if len(self._limit_value_list) == 0:
            return

        for row_item in rows:
            self._check_limits(row_item)

    @property
    def probable_type(self):
        return self._probable_type

    @property
    def limit_value_list(self):
        return self._limit_value_list


# DATA SEGMENT END.
# endregion
#
# ----- SOURCE END -----
