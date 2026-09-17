from typing import Final

# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> CONFIGURATION GRAMMAR VALUE TYPE.
#
# INTRODUCTION SENTENCE。
# -> This source file is used to define the configuration grammar value's type.
# -> Because this language is a high types language, so it need to define the type of the configuration grammar value.
# -> From that, the configuration grammar value can be used in the configuration grammar, and the configuration grammar can be used in the configuration file.
# -> For example, it is included: list, database, int, string, boolean, bytes (only one), etc.
# -> Furthermore, it will also take on some read only function to help to get the information about multiple part.
#
# GLOBAL VALUE SEGMENT START.

LEGAL_STRING_WORD: Final[str]     = "abcdefghijklmnopqrstuvwxyz1234567890-_"
STATUS_CHAR:       Final[str]     = "_"
CALCULATE_CHAR:    frozenset[str] = frozenset({"+", "-", "*", "/", "**", "//", "<<", ">>", "&", "|", "^"})


class ConfigurationValueType:   # noqa
    # +------------+-------------+-------------+--------------------------+
    # |    NAME    |    TYPE     |   VALUE     |         EXPLAIN          |
    # +------------+-------------+-------------+--------------------------+
    VALUE_TABLE:      Final[str] = "table"       # Stated the child part of the configuration, and it is a table which can contain multiple child part.
    VALUE_DATABASE:   Final[str] = "database"    # Stated the child database part of the configuration.
    VALUE_INT:        Final[str] = "int"         # A simple integer value.
    VALUE_FLOAT:      Final[str] = "float"       # A simple decimal number value.
    VALUE_STRING:     Final[str] = "string"      # A simple string value.
    VALUE_BOOL:       Final[str] = "bool"        # As you know, it is a simple boolean value.
    VALUE_FILE:       Final[str] = "file"        # It looks like a string, but when load the file, it will return the target file IO rather than string.
    VALUE_ENUM:       Final[str] = "enum"        # It's similar to "-> LIMIT TO [1, 2, 3, 4, 5, ...]", but I add this to give another choice for programmer to make it readable.
    VALUE_UNION:      Final[str] = "union"       # When some value has multiple value types, you can use this to include all of them except to use "ANYTHING" type.
    ANYTHING_VALUE:   Final[str] = "anything"    # When you don't care about the value type, you can use this keyword to state it, and it will return the value with the original type in the configuration file.
    CONVERSION_VALUE: Final[str] = "conversion"  # This is a special complex value. You can use this to build a mutable value which changed by some rule.
    # +------------+-------------+-------------+--------------------------+

    def __str__(self) -> list[str]:
        return [
            self.VALUE_TABLE, self.VALUE_DATABASE, self.VALUE_INT, self.VALUE_ENUM,
            self.VALUE_FLOAT, self.VALUE_STRING, self.VALUE_BOOL, self.VALUE_FILE,
            self.ANYTHING_VALUE, self.CONVERSION_VALUE,
        ]

# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> CONFIGURATION KEYWORD SENTENCE TYPE.
#
# INTRODUCE SENTENCE.
# -> This is used to define the configuration keyword sentence's type.
# -> As a consequence of that I want to make this configuration language realize some complex function, so I need to define some keyword sentence type to make the configuration grammar more powerful.
# -> Well...I get this idea from a vintage computer language named...COBOL.
# -> From keyword, it don't care about the writing type is lower or upper.
#
# GLOBAL VALUE SEGMENT START.


class ConfigurationKeyword:   # noqa
    # +-----------------------+----------------+-------------------------+--------------------------+
    # |        NAME           |      TYPE      |          VALUE          |         EXPLAIN          |
    # +-----------------------+----------------+-------------------------+--------------------------+
    KEYWORD_IDENTIFICATION:     Final[str]     = "identification"           # Every part in the configure file need to statement, you can use it to do it.
    KEYWORD_CONFIGURE_ID:       Final[str]     = "configuration-id"         # It is used to state the configuration id, and it is a string value.
    KEYWORD_CONFIGURE_VERSION:  Final[str]     = "configuration-version"    # It is used to realize this config file follow the rule's version, and it is a double value with one decimal. You can use this to support old config file.
    KEYWORD_CONFIGURE_READONLY: Final[str]     = "configuration-readonly"   # It is used to state the configuration readonly, and it is a boolean value. You can use "true" or "false" (or also not zero's number and zero's number) to state it.
    KEYWORD_CONFIGURE_ENCODE:   Final[str]     = "configuration-encode"     # It is used to state the configuration encode, and it is a string value.
    KEYWORD_DATABASES_START:    Final[str]     = "databases-start"          # Mark the start of the databases part, and it is used to separate the databases part and the content part.
    KEYWORD_DATABASES_END:      Final[str]     = "databases-end"            # Mark the end of the databases part, and it is used to separate the databases part and
    KEYWORD_CONVERSION_START:   Final[str]     = "conversion-start"         # Mark the start of the conversion rule part, and it is used to separate the conversion rule part and the content part.
    KEYWORD_CONVERSION_END:     Final[str]     = "conversion-end"           # Mark the end of the conversion rule part, and it is used to separate the conversion rule part and the content part.
    # +-----------------------+----------------+-------------------------+--------------------------+

    def __list__(self) -> list[str]:
        return [
            self.KEYWORD_IDENTIFICATION, self.KEYWORD_CONFIGURE_ID, self.KEYWORD_CONFIGURE_VERSION,
            self.KEYWORD_CONFIGURE_ENCODE, self.KEYWORD_CONFIGURE_READONLY, self.KEYWORD_CONFIGURE_ENCODE,
            self.KEYWORD_DATABASES_START, self.KEYWORD_DATABASES_END,
            self.KEYWORD_CONVERSION_START, self.KEYWORD_CONVERSION_END,
        ]


# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> CONFIGURATION EXECUTIVE KEYWORD.
#
# INTRODUCE SENTENCE.
# -> This is used to define the configuration executive keyword which can executive some function.
# -> Because sometimes some value need to state extend requirement, so thoes keyword can help on it.
# -> For example, when you need to call some function in the configuration, you can use the "call" keyword to realize it.
# -> Maybe you are questioning that why I need to writedown so much keyword and just to call a function?
# -> Well...It can make the configure file more readable and more powerful, and it can also make the configure file more like a programming language, so it can be easier to understand and use.
#
# GLOBAL VALUE SEGMENT START.


class ConfigurationDataExecutiveKeyword:   # noqa
    # +-----------------------+------------+---------------+--------------------------+
    # |        NAME           |    TYPE    |     VALUE     |        EXPLAIN           |
    # +-----------------------+------------+---------------+--------------------------+
    EXECUTIVE_KEYWORD_RETURN:   Final[str] = "return"       # When you need to return some value in the configuration, you can use this keyword to realize it.
    EXECUTIVE_KEYWORD_COMPARE:  Final[str] = "compare"      # You can use this keyword to compare some value's status, which will return a bool value. Because it needs to be used in some special place, so I isolated it from 'return'.
    EXECUTIVE_KEYWORD_MUTABLE:  Final[str] = "mut"          # To use this keyword, means you agree some value in the database can be change and rewrite, and it will return a mutable value rather than an immutable value.
    EXECUTIVE_KEYWORD_CONST:    Final[str] = "cst"          # To use this keyword, means you agree some value in the database can't be change and rewrite, and it will return an immutable value rather than a mutable value. Also, this is the default type in the configuration, so if you don't use the "mut" keyword, it will return an immutable value rather than a mutable value.
    EXECUTIVE_KEYWORD_SUMMARY:  Final[str] = "sum"          # When you need to summary some value in the configuration, you can use this keyword to realize it.
    EXECUTIVE_KEYWORD_TO:       Final[str] = "to"           # This is make sure easy to read, and separating the range of data.
    EXECUTIVE_KEYWORD_CALL:     Final[str] = "call"         # When you need to call some function in the configuration, you can use this keyword to realize it.
    # +-----------------------+------------+---------------+--------------------------+

    def __list__(self) -> list[str]:
        """
        When print this class, it will return all the keyword in here.
        :return: list[str]
        """
        return [
            self.EXECUTIVE_KEYWORD_RETURN, self.EXECUTIVE_KEYWORD_MUTABLE,
            self.EXECUTIVE_KEYWORD_CONST, self.EXECUTIVE_KEYWORD_SUMMARY,
            self.EXECUTIVE_KEYWORD_COMPARE, self.EXECUTIVE_KEYWORD_TO,
            self.EXECUTIVE_KEYWORD_CALL
        ]


# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> CONFIGURATION DATA STATUS KEYWORD.
#
# INTRODUCE SENTENCE.
# -> This class defines all the status keyword in the configuration grammar.
# -> Because sometimes some value need to state extend requirement, so thoes keyword can help on it.
# -> Maybe you could use '1' or '0' to realize approximate function, but use thoes keyword can make the code more readable.
#
# GLOBAL VALUE SEGMENT START.

class ConfigurationStatusExecutiveKeyword:   # noqa
    # +------------------------+------------+------------+--------------------------+
    # |         NAME           |    TYPE    |   VALUE    |      EXPLAIN             |
    # +------------------------+------------+------------+--------------------------+
    STATUS_EXEC_KEYWORD_TRUE:    Final[str] = "true"       # A simple keyword means the boolean value named "True".
    STATUS_EXEC_KEYWORD_FALSE:   Final[str] = "false"      # A simple keyword means the boolean value named "False".
    STATUS_EXEC_KEYWORD_NULL:    Final[str] = "null"       # You can use this keyword to keep some value empty, and it will return None when load the configuration file.
    STATUS_EXEC_KEYWORD_FORMAT:  Final[str] = "format"     # This is a placeholder keyword. When you need to use this, you can input the format string to change it (also CST is okay, but you cannot write down it.)
    STATUS_EXEC_KEYWORD_DEFAULT: Final[str] = "default"    # When set the rule, you can use this keyword to build an executive with default's sentence. Otherwise, if you try to push it into a value, please make sure this value is supported this method, or it will cause the error.
    STATUS_EXEC_KEYWORD_EXCLUDE: Final[str] = "exclude"    # When set the rule, you can use this keyword to build an executive with excludes sentence. Otherwise, if you try to push it into a value, please make sure this value is supported this method, or it will cause the error.
    # +------------------------+------------+------------+--------------------------+

    def __list__(self) -> list[str]:
        """
        When print this class, it will return all the keyword in here.
        :return: list[str]
        """
        return [
            self.STATUS_EXEC_KEYWORD_TRUE, self.STATUS_EXEC_KEYWORD_FALSE,
            self.STATUS_EXEC_KEYWORD_NULL, self.STATUS_EXEC_KEYWORD_FORMAT,
            self.STATUS_EXEC_KEYWORD_DEFAULT, self.STATUS_EXEC_KEYWORD_EXCLUDE
        ]
# GLOBAL VALUE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> CONFIGURATION CONVERSION DEFINE KEYWORD.
#
# INTRODUCE SENTENCE.
# -> Well...of cource I understand that you want to save some complex value, so I made this!
# -> When you need to load some complex value and don't want to save a mountan of value to try to discribe this,
# -> You can statement a conversion value which will be changed in auto follow the rule you defined.
# -> Afterwords, build a simple inferencial formula or estimational formula to do it.
#
# GLOBAL VALUE SEGMENT START.


class ConfigurationConversionKeyword(object):
    # +------------------------------+----------------+-----------------+-------------------------------------------+
    # |             NAME             |      TYPE      |     VALUE       |                   EXPLAIN                 |
    # +------------------------------+----------------+-----------------+-------------------------------------------+
    WITH_KEYWORD_TIME_CONVERSION:      Final[str]     = "with-time"        # Value's change is follow the time. It will return a database value with some int value.
    WITH_KEYWORD_MACHINE_CONVERSION:   Final[str]     = "with-machine"     # Value's change is follow the local machine. It will return a database value with some string value.
    WITH_KEYWORD_PATH_CONVERSION:      Final[str]     = "with-path"        # Value's change is follow the software's path. It will return a database value with some string value.
    WITH_KEYWORD_LOCALE_CONVERSION:    Final[str]     = "with-locale"      # Value's change is follow the place where user are. It will return a unidimensional table with two int value.
    WITH_KEYWORD_LANGUAGE_CONVERSION:  Final[str]     = "with-language"    # Value's change is follow the language which user is using.
    WITH_KEYWORD_NETWORK_CONVERSION:   Final[str]     = "with-network"     # Value's change is follow the network's connection status.
    WITH_KEYWORD_COUNTDOWN_CONVERSION: Final[str]     = "with-count"       # Value's change is follow the read's count, it will return an int value.
    WITH_KEYWORD_VALUE_CONVERSION:     Final[str]     = "with-value"       # You can use only one default function and return the value with the value which it returned to compare and return the different value.
    # +------------------------------+----------------+-----------------+-------------------------------------------+

    def __list__(self) -> list[str]:
        return [
            self.WITH_KEYWORD_TIME_CONVERSION, self.WITH_KEYWORD_MACHINE_CONVERSION,
            self.WITH_KEYWORD_PATH_CONVERSION, self.WITH_KEYWORD_LOCALE_CONVERSION,
            self.WITH_KEYWORD_LANGUAGE_CONVERSION, self.WITH_KEYWORD_NETWORK_CONVERSION,
            self.WITH_KEYWORD_COUNTDOWN_CONVERSION, self.WITH_KEYWORD_VALUE_CONVERSION,
        ]


# GLOBAL VALUE SEGMENT END.
# 
# IDENTIFICATION END.
# endregion
# 
# ----- SEPARATING LINE -----
# 
# region
# IDENTIFICATION GLOBAL VALUE. TO >>> EXTENSION KEYWORD SETTER.
# 
# INTRODUCE SENTENCE.
# -> This file's part is used to
# -> 
# -> 
# 
# GLOBAL VALUE SEGMENT START.


class ConfigurationExtensionKeyword(object):
    EXECUTIVE_KEYWORD_LIMIT:    Final[str] = "limit"        # When you need to limit the value of one part, you can use this keyword to realize it.
    EXECUTIVE_KEYWORD_REGULAR:  Final[str] = "regular"      # You can use this to match and compare the complex string with regular expression. It will return a NoneType value when never find target data.

    def __list__(self) -> list[str]:
        return [self.EXECUTIVE_KEYWORD_LIMIT, self.EXECUTIVE_KEYWORD_REGULAR]


# GLOBAL VALUE SEGMENT END.
# 
# IDENTIFICATION END.
# endregion
#
# ----- SEPARATING LINE -----
#
# IDENTIFICATION GLOBAL VALUE. TO >>> INNER PACKAGE VALUE.
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


class ConfigurationInnerPackage(object):
    INNER_PACKAGES:   Final[str] = "packages"
    INNER_MATHMATICS: Final[str] = "mathmatics"

    def __list__(self) -> list[str]:
        return [
            self.INNER_PACKAGES, self.INNER_MATHMATICS
        ]


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
