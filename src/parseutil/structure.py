# VALUE SAVING STRUCTURE

import ctypes
from typing import Any

from src.parseutil.kword import CALCULATE_CHAR
from src.parseutil.signal import ValueFormatter
from src.parsefunc.function import isinstance_loose, ConversionDecimal
from src.parseutil.signal import TypeExplainFormatter
from src.parseutil.column import calculate_dispose


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
                for list_item in value:
                    for index, value_item in enumerate(list_item):
                        if not isinstance_loose(value_item, self._probable_type[index]):
                            return False

                # Or anything else. so we can return the truth.
                return True

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
            case LimitExplainFormatter.LIMIT_WITHIN_VALUE:              return value == limit_element[0]                                   # noqa
            case LimitExplainFormatter.LIMIT_WITHOUT_VALUE:             return value != limit_element[0]                                   # noqa

            # Limit with string regular, on here it will change it into the string, and try to match it is in the rule or not.
            case LimitExplainFormatter.LIMIT_WITH_STRING_REGULAR:        return re.match(limit_element[0], str(value)) is not None         # noqa
            case LimitExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR:     return re.match(limit_element[0], str(value)) is None             # noqa

            # Limit with condition rule, welp...just means this is the left limit or the right limit.
            case LimitExplainFormatter.LIMIT_WITHIN_CONDITION_RULE:       return limit_element[0][0] < value < limit_element[0][1]         # noqa
            case LimitExplainFormatter.LIMIT_WITHOUT_CONDITION_RULE:      return not limit_element[0][1] < value < limit_element[0][2]     # noqa

            # Just with in the equal.
            case LimitExplainFormatter.LIMIT_WITHIN_CONDITION_AND_EQUAL:  return limit_element[0][0] >= value >= limit_element[0][1]       # noqa
            case LimitExplainFormatter.LIMIT_WITHOUT_CONDITION_AND_EQUAL: return not limit_element[0][1] >= value >= limit_element[0][2]   # noqa

            # Welp...So has this line of code can be occurred?
            case _:
                return False

    @staticmethod
    def _calculate(value: list[tuple[Any, ctypes.c_uint8]]) -> Any:
        stack_load: list[Any] = []
        for item in value:
            if isinstance(item[0], str) and item[0] in CALCULATE_CHAR:
                second_value: tuple[Any, ctypes.c_uint8] = stack_load.pop()
                first_value:  tuple[Any, ctypes.c_uint8] = stack_load.pop()
                stack_load.append(calculate_dispose(first_value, second_value, item[0]))
            else:
                stack_load.append(item[0])
        return stack_load[0]

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
        push_value: Any = self._calculate(self._value)
        return float(push_value) if isinstance_loose(push_value, ConversionDecimal) else push_value

    @value.setter
    def value(self, new_value: list[tuple[Any, ctypes.c_uint8]]) -> None:
        if not self._changeable:  # Check the changeable.
            raise InterruptedError("This is a read-only value.")
        calc: Any = self._calculate(new_value)

        # Check the type and limit, make sure it's valid.
        if not self._check_in_type(calc):
            raise TypeError("Error type of the value in here.")
        if len(self._limit_value_list) > 0:
            for limit_item in self._limit_value_list:
                if self._check_in_limit(calc, limit_item):
                    break
            else:  # When not break, we can raise the error means this is breaking the limit rule.
                raise ValueError("This value is in the limit list's rule, please check and change the rule.")

        # Or nothing limit in here, so we can just add it into the value part.
        self._value = new_value

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
