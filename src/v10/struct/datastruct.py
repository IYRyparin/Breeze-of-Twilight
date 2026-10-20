# VALUE SAVING STRUCTURE

from typing import Any


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
# -> So...I build a middle proxy from Python and Breeze of Twilight,
# -> it can get the executive code from Python and call target part of BOT.
#
# DATA SEGMENT START.


class ConfigNodeHeaderStructure(object):
    CONFIGURATION_ID: str = ""
    CONFIGURATION_VERSION: float = 0.0
    CONFIGURATION_READONLY: bool = False
    CONFIGURATION_ENCODE: str = "utf-8"
    config_filepath: str = "N/A"


class ConfigurationDataItemStructure(object):
    probable_type:  tuple[str | list | Any, int]
    value:          list[tuple[Any, int]]
    changeable:     bool
    limit_list:     list[tuple[Any, int]]


class ConfigurationValueStructure(object):
    value: list[tuple[Any, int]]


class ConfigurationConversionStructure(object):
    return_type:     tuple[str | list | Any, int]
    follow_function: tuple[Any, int]


# DATA SEGMENT END.
# endregion
#
# ----- SOURCE END -----
