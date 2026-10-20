import dataclasses
from typing import Final


@dataclasses.dataclass(frozen=True)
class ConfigurationTypeKeyword(object):
    TABLE:      Final[str] = "table"       # Stated the child part of the configuration, and it is a table which can contain multiple child part.
    DATABASE:   Final[str] = "database"    # Stated the child database part of the configuration.
    INT:        Final[str] = "int"         # A simple integer value.
    FLOAT:      Final[str] = "float"       # A simple decimal number value.
    STRING:     Final[str] = "string"      # A simple string value.
    BOOL:       Final[str] = "bool"        # As you know, it is a simple boolean value.
    FILE:       Final[str] = "file"        # It looks like a string, but when load the file, it will return the target file IO rather than string.
    ENUM:       Final[str] = "enum"        # It's similar to "-> LIMIT TO [1, 2, 3, 4, 5, ...]", but I add this to give another choice for programmer to make it readable.
    UNION:      Final[str] = "union"       # When some value has multiple value types, you can use this to include all of them except to use "ANYTHING" type.
    ANYTHING:   Final[str] = "anything"    # When you don't care about the value type, you can use this keyword to state it, and it will return the value with the original type in the configuration file.
    CONVERSION: Final[str] = "conversion"  # This is a special complex value. You can use this to build a mutable value which changed by some rule.

    def __list__(self) -> list[str]:
        return [
            self.TABLE, self.DATABASE, self.INT, self.ENUM,
            self.FLOAT, self.STRING, self.BOOL, self.FILE,
            self.ANYTHING, self.CONVERSION,
        ]


class ConfigurationChangeableKeyword(object):
    CONSTANT: Final[str] = "cst"
    MUTABLE:  Final[str] = "mut"

    def __list__(self) -> list[str]:
        return [self.CONSTANT, self.MUTABLE]


@dataclasses.dataclass(frozen=True)
class ConfigurationValueReplacerKeyword:
    TRUE:  Final[str] = "true"          # A simple keyword means the boolean value named "True".
    FALSE: Final[str] = "false"         # A simple keyword means the boolean value named "False".
    NULL:  Final[str] = "null"          # You can use this keyword to keep some value empty, and it will return None when load the configuration file.
    INF:   Final[str] = "infinite"      # A special value, explain the 'infinite' special part.
    NAN:   Final[str] = "not_a_number"  # A special value, explain the 'not a number' special part.

    def __list__(self) -> list[str]:
        return [
            self.TRUE, self.FALSE,
            self.NULL, self.INF, self.NAN,
        ]


@dataclasses.dataclass(frozen=True)
class ConfigurationValueRequireSentencesKeyword(object):
    FORMAT:  Final[str] = "format"   # This is a placeholder keyword. When you need to use this, you can input the format string to change it (also CST is okay, but you cannot write down it.)
    DEFAULT: Final[str] = "default"  # When set the rule, you can use this keyword to build an executive with default's sentence. Otherwise, if you try to push it into a value, please make sure this value is supported this method, or it will cause the error.
    EXCLUDE: Final[str] = "exclude"  # When set the rule, you can use this keyword to build an executive with excludes sentence. Otherwise, if you try to push it into a value, please make sure this value is supported this method, or it will cause the error.
    CALL:    Final[str] = "call"     # When set the rule, you can use this keyword to build an executive with call's sentence. Otherwise, if you try to push it into a value, please make sure this value is supported this method, or it will cause the error.
    RETURN:  Final[str] = "return"   # When you need to return some value in the configuration, you can use this keyword to realize it.
    COMPARE: Final[str] = "compare"  # You can use this keyword to compare some value's status, which will return a bool value. Because it needs to be used in some special place, so I isolated it from 'return'.
    SUMMARY: Final[str] = "sum"      # When you need to summary some value in the configuration, you can use this keyword to realize it.
    TO:      Final[str] = "to"       # This is make sure easy to read, and separating the range of data.
    REDUCE:  Final[str] = "reduce"   # When use '1.0 TO 4.0', you can use this to let parser know how much it need to reduce the fraction.
    THEN:    Final[str] = "then"     # A transition keyword, used to tell the parser that need to prepare for the next part of parsing.

    def __list__(self) -> list[str]:
        return [
            self.FORMAT, self.DEFAULT,
            self.EXCLUDE, self.CALL,
            self.RETURN, self.COMPARE,
            self.SUMMARY, self.TO, self.REDUCE, self.THEN
        ]


@dataclasses.dataclass(frozen=True)
class ConfigurationConversionFollowRuleKeyword(object):
    WITH_TIME:      Final[str] = "with_time"        # Value's change is follow the time. It will return a database value with some int value.
    WITH_MACHINE:   Final[str] = "with_machine"     # Value's change is follow the local machine. It will return a database value with some string value.
    WITH_PATH:      Final[str] = "with_path"        # Value's change is follow the software's path. It will return a database value with some string value.
    WITH_LOCALE:    Final[str] = "with_locale"      # Value's change is follow the place where user are. It will return a unidimensional table with two int value.
    WITH_LANGUAGE:  Final[str] = "with_language"    # Value's change is follow the language which user is using.
    WITH_NETWORK:   Final[str] = "with_network"     # Value's change is follow the network's connection status.
    WITH_COUNTDOWN: Final[str] = "with_count"       # Value's change is follow the read's count, it will return an int value.
    WITH_VALUE:     Final[str] = "with_value"       # You can use only one default function and return the value with the value which it returned to compare and return the different value.

    def __list__(self) -> list[str]:
        return [
            self.WITH_TIME, self.WITH_MACHINE,
            self.WITH_PATH, self.WITH_LOCALE,
            self.WITH_LANGUAGE, self.WITH_NETWORK,
            self.WITH_COUNTDOWN, self.WITH_VALUE,
        ]


@dataclasses.dataclass(frozen=True)
class ConfigurationDefineKeyword(object):
    IDENTIFICATION:     Final[str]     = "identification"           # Every part in the configure file need to statement, you can use it to do it.
    CONFIGURE_ID:       Final[str]     = "configuration_id"         # It is used to state the configuration id, and it is a string value.
    CONFIGURE_VERSION:  Final[str]     = "configuration_version"    # It is used to realize this config file follow the rule's version, and it is a double value with one decimal. You can use this to support old config file.
    CONFIGURE_READONLY: Final[str]     = "configuration_readonly"   # It is used to state the configuration readonly, and it is a boolean value. You can use "true" or "false" (or also not zero's number and zero's number) to state it.
    CONFIGURE_ENCODE:   Final[str]     = "configuration_encode"     # It is used to state the configuration encode, and it is a string value.
    DATABASES_START:    Final[str]     = "databases_start"          # Mark the start of the databases part, and it is used to separate the databases part and the content part.
    DATABASES_END:      Final[str]     = "databases_end"            # Mark the end of the databases part, and it is used to separate the databases part and
    CONVERSION_START:   Final[str]     = "conversion_start"         # Mark the start of the conversion rule part, and it is used to separate the conversion rule part and the content part.
    CONVERSION_END:     Final[str]     = "conversion_end"           # Mark the end of the conversion rule part, and it is used to separate the conversion rule part and the content part.

    def __list__(self) -> list[str]:
        return [
            self.IDENTIFICATION, self.CONFIGURE_ID, self.CONFIGURE_VERSION,
            self.CONFIGURE_ENCODE, self.CONFIGURE_READONLY, self.CONFIGURE_ENCODE,
            self.DATABASES_START, self.DATABASES_END,
            self.CONVERSION_START, self.CONVERSION_END,
        ]


@dataclasses.dataclass(frozen=True)
class ConfigurationExtensionKeyword(object):
    LIMIT:    Final[str] = "limit"    # When you need to limit the value of one part, you can use this keyword to realize it.
    REGULAR:  Final[str] = "regular"  # You can use this to match and compare the complex string with regular expression. It will return a NoneType value when never find target data.

    def __list__(self) -> list[str]:
        return [self.LIMIT, self.REGULAR]


@dataclasses.dataclass(frozen=True)
class ConfigurationInnerPackageKeyword(object):
    INNER_PACKAGES:    Final[str] = "packages"
    INNER_MATHEMATICS: Final[str] = "mathematics"

    def __list__(self) -> list[str]:
        return [self.INNER_PACKAGES, self.INNER_MATHEMATICS]
