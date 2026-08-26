# VALUE SAVING STRUCTURE

import ctypes
from typing import Any

from src.parsefunc.function import isinstance_loose, Counter
from src.parseutil.column import complex_data_type_checker
from src.parseutil.kword import ConfigurationStatusExecutiveKeyword
from src.parseutil.signal import TypeExplainFormatter


# ----- SOURCE START -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> ASSISTANT DATABASE.
#
# region
# INTRODUCE SENTENCE.
# -> This code segment is used to define the data structure,
# -> which will be used to save the critical information which will be used to execute the BOT file.
# -> Because of the complex method, we may break some part of the string.
# -> To use this, we can save the origin signal from the data's part which may be broken,
# -> and we can use it to restore the string when we need to call it.
# -> So from that, I build this code segment to realize it.
#
# DATA SEGMENT START.


class ConfigurationSignalStructure(object):
    # +------------------------------+------------+------------+-------------------------+
    # |            NAME              |    TYPE    |   VALUE    |         EXPLAIN         |
    # +------------------------------+------------+------------+-------------------------+
    _signal_in_data_type:              bool       = False
    _signal_in_data_value:             bool       = False
    _signal_in_data_extension_require: bool       = False
    # +------------------------------+------------+------------+-------------------------+

    def __str__(self) -> str:
        """
        When call by string, return the data's information with dictionary type.
        :return: str
        """
        return str(self.__dict__)

    def __getitem__(self, key: str) -> bool:
        """
        When call by dictionary, return the data's information with dictionary type.
        :param key: str   Target data string.
        :return: bool
        """
        match key:
            case "type":              return self._signal_in_data_type                           # noqa
            case "value":             return self._signal_in_data_value                          # noqa
            case "extension_require": return self._signal_in_data_extension_require              # noqa
            case _:                   raise KeyError(f"Illegal type: {key}, please try again.")  # noqa

    def __check_state__(self) -> bool:
        """
        This method is used to check configuration's signal.
        Because of mutually exclusion in the signal, so we need to check it when we need to use it.
        :return: bool
        """
        return not sum(
            [self._signal_in_data_type, self._signal_in_data_value, self._signal_in_data_extension_require]) > 1

    @property
    def signal_in_data_type(self) -> bool:
        """
        Return the target value of signal_in_data_type.
        :return: bool
        """
        return self._signal_in_data_type

    @signal_in_data_type.setter
    def signal_in_data_type(self, value: bool) -> None:
        """
        Set the target value of signal_in_data_type.
        :param value: bool   Target value of signal_in_data_type.
        :return: None
        """
        if not isinstance(value, bool):  # At first, we need to make sure that this value is followed correct type.
            raise TypeError(f"Illegal type: {value}, it must be a boolean value, please try again.")

        # After that, virtually the new statue and start to check the value's information and set the value.
        self._signal_in_data_type = value
        if not self.__check_state__():  # Check the value, if not supported, raise the exception and change the value.
            self._signal_in_data_type = not self._signal_in_data_type
            raise KeyError(f"Illegal type: {value}, Only support one True value.")

    @property
    def signal_in_data_value(self) -> bool:
        """
        Return the target value of signal_in_data_value.
        :return: bool
        """
        return self._signal_in_data_value

    @signal_in_data_value.setter
    def signal_in_data_value(self, value: bool) -> None:
        """
        Set the target value of signal_in_data_value.
        :param value: bool   Target value of signal_in_data_value.
        :return: None
        """
        if not isinstance(value, bool):  # At first, we need to make sure that this value is followed correct type.
            raise TypeError(f"Illegal type: {value}, it must be a boolean value, please try again.")

        # After that, virtually the new statue and start to check the value's information and set the value.
        self._signal_in_data_value = value

        # Check the value, if not supported, raise the exception and change the value.
        if not self.__check_state__():
            self._signal_in_data_value = not self._signal_in_data_value
            raise KeyError(f"Illegal type: {value}, Only support one True value.")

    @property
    def signal_in_data_extension_require(self) -> bool:
        """
        Return the target value of signal_in_data_extension_require.
        :return: bool
        """
        return self._signal_in_data_extension_require

    @signal_in_data_extension_require.setter
    def signal_in_data_extension_require(self, value: bool) -> None:
        """
        Set the target value of signal_in_data_extension_require.
        :param value: bool   Target value of signal_in_data_extension_require.
        :return: None
        """
        if not isinstance(value, bool):
            raise TypeError(f"Illegal type: {value}, it must be a boolean value, please try again.")

        # After that, virtually the new statue and start to check the value's information and set the value.
        self._signal_in_data_extension_require = value
        if not self.__check_state__():  # Check the value, if not supported, raise the exception and change the value.
            self._signal_in_data_extension_require = not self._signal_in_data_extension_require
            raise KeyError(f"Illegal type: {value}, Only support one True value.")


# DATA SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION GLOBAL CLASS. TO >>> LANGUAGE PARSER.
#
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
        self._value:              Any                               = None                        # Final value of the element.
        self._format:             ctypes.c_uint8                    = ctypes.c_uint8(0x00)        # Value and segment's format of the element.
        self._changeable:         bool                              = True                        # A signal, used to means that this value can be changed or not.
        self._limit_value_list:   set[tuple[Any, ctypes.c_uint8]]   = set()                       # Which value you want to reject or accept.
        self._value_origin:       str                               = ""                          # Original value's string of the element.
        self._multi_loader:       list[tuple[int, bool]]            = []                          # A list used to format the value when program is running. It's load with two value, means the format signal's index, and can be changed manually or not.
        self._str_memory_pointer: list[str]                         = []
        self._str_mem_counter:    Counter                           = Counter(0)
        # +----------------------+----------------------------------+---------------------------+-----------------------------------+

    # IDENTIFICATION SEGMENT PART. TO >>> BASIC VALUE SETTER SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
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
        return self._value

    @value.setter
    def value(self, new_value: Any) -> None:
        if not self._changeable:  # Check the changeable.
            raise InterruptedError("This is a read-only value.")

        # Check the type.
        if not self._check_in_type(new_value):
            raise TypeError("Not supported value's type.")

        # After checking, so we can start to check it is in the limit list or not.
        for limit_item in self._limit_value_list:
            if self._check_in_limit(new_value, limit_item):
                self._value = new_value
                break

        # When not break, we can raise the error means this is breaking the limit rule.
        else:
            raise ValueError("This value is in the limit list's rule, please check and change the rule.")

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> BASIC FORMAT EXECUTIVE SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START

    def format_init(self) -> None:
        """
        This function is used to check the format signal's information.
        When we meet the format signal, we can load the probable default value into the multi loader list.
        So from here, the value can have more multiple useful functions.
        :return: None
        """
        temp_string_memory: str  = ""     # Temp memory to load the string.
        string_signal:      bool = False  # Means that we are in the string (ignore) or not.
        value_origin_index: int  = 0      # Local index.

        # At first, we can check the double index.
        if self._value_origin.startswith("\""):
            string_signal = True

        # Start to check the format signal's information.
        while value_origin_index < len(self._limit_value_list):
            value_origin_index += 1  # Increase the index.

            # Load the char into the memory.
            value_origin_char: str = self._value_origin[value_origin_index]

            # Check the string signal.
            if value_origin_char == "\"" and self._value_origin[value_origin_index - 1] != "\\":
                string_signal = not string_signal
                continue

            # Load terminate signal, start to check the string.
            if value_origin_char == " " and not string_signal and temp_string_memory != "":
                if temp_string_memory.strip() == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_FORMAT:
                    default_final_index: int = self._value_origin.find(" ", value_origin_index)

                    # Find next keyword's probably locale, start to check the probable keyword's information.
                    if self._value_origin[default_final_index : default_final_index + 7] == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_DEFAULT:  # noqa
                        default_final_index = self._value_origin.find(" ", default_final_index + 7)

                        # When we meet the value, we can start the next check.
                        default_string_signal:      bool = False
                        default_temp_string_memory: str  = ""
                        final_default_value:        Any

                        # Start the check.
                        while self._value_origin[default_final_index] != " " and not default_string_signal:
                            default_final_index        += 1
                            default_temp_string_memory += self._value_origin[default_final_index]

                            # Check the string signal.
                            if self._value_origin[default_final_index] == "\"" and self._value_origin[default_final_index - 1] != "\\":
                                default_string_signal = not default_string_signal
                                continue

                        # So now, we get the probable default value, we can check it is in the limit list or not.
                        if isinstance(complex_data_type_checker(default_temp_string_memory), str):
                            final_default_value    = self._str_memory_pointer[self._str_mem_counter]  # Get the string from the memory pointer.
                            temp_loader: list[str] = list(self._value)                                # Load the value into the temp loader.

                            # Start to change the value.
                            del temp_loader[value_origin_index : default_final_index]  # noqa
                            temp_loader.insert(value_origin_index, final_default_value)

                            # Save the value into the memory pointer.
                            self._value = ''.join(temp_loader)

                        # Not the string type, just check and convert it into the target type.
                        else:
                            self._value = complex_data_type_checker(default_temp_string_memory)[0]

                    # Or anything else, means that there is no default keyword, so we can just continue normally.
                    else:
                        pass

                    # Load the format index and the final value into the multi loader list.
                    self._multi_loader.append((value_origin_index - 6, True))

                    # All is ok, flush the temp string memory and continue to check the next char.
                    temp_string_memory = ""
                    value_origin_index = default_final_index
                    continue

    def format_insert(self, *args: Any) -> None:
        """
        This function is used to insert the value into the multi loader list.
        :param args: Any   Target value's information.
        :return: None
        """
        ...

    # CODE SEGMENT PART END.
    # endregion
    @property
    def probable_type(self):
        return self._probable_type

# DATA SEGMENT END.
# endregion
#
# ----- SOURCE END -----
