from typing import Any, Final
from queue import Queue

from src.v10.struct.signal import TypeExplainFormatter
from src.v10.valchk.strchk.contain import brackets_edge_index_checker
from src.v10.valchk.anychk.autochk import scalar_value_loader
from src.v10.valchk.strchk.splitter import split_top_level_string
from src.v10.struct.kword import ConfigurationTypeKeyword


class DatabasesSegmentTypeChecker(object):  # Final solution...
    def __init__(self) -> None:
        """
        :return: None
        """
        pass

    def dict_checker(self, string: str) -> Any:
        checking_dictionary: Final[dict[str, Any]] = {
            # +---------------+--------------------------------------+
            # |      KEY      |                VALUE                 |
            # +---------------+--------------------------------------+
            "int":              self.int_segment_type_checker,
            "string":           self.string_segment_type_checker,
            "float":            self.float_segment_type_checker,
            "bool":             self.bool_segment_type_checker,
            "database":         self.databases_segment_type_checker,
            "file":             self.file_segment_type_checker,
            "anything":         self.anything_segment_type_checker,
            "enum":             self.enum_segment_type_checker,
            "table":            self.table_segment_type_checker,
            "union":            self.union_segment_type_checker,
            "conversion":       self.conversion_segment_type_checker,
            "list":             self.list_segment_type_checker
            # +---------------+--------------------------------------+
        }
        key = string.strip()

        # Common shorthand aliases mapping.
        aliases: dict[str, str] = {
            'str': 'string', 'dbl': 'float', 'flt': 'float',
            'boolean': 'bool', 'db': 'database', 'tbl': 'table',
            'lst': 'list', 'any': 'anything', 'conv': 'conversion',
            'uni': 'union', 'enm': 'enum', 'file_path': 'file'
        }
        if key in aliases:
            key = aliases[key]
        key_head: str = key if key.find("<") == -1 else key[:key.find("<")]

        # Return the correct value (function pointer).
        if key_head not in set(checking_dictionary.keys()):
            raise KeyError(f"Unsupported configuration data type: {string.strip()!r}")

        return checking_dictionary[key_head]

    def resolve_type(self,
                     dat_info_string: str,
                     full_string: str,
                     queue_loader: Queue[tuple[str, int]]) -> tuple[str | list, int]:
        """
        Resolve one type word (with its parameters) into concrete python types.

        `dict_checker` only hands back the *checker callable*, which is what the parser needs
        for the statement level, while every place that needs the real type list (tables,
        unions, nested declarations) must go resolving through this helper instead.

        :param queue_loader: A queue which saved the string value.
        :param dat_info_string: Full type word, e.g. "int" or "table<int, str>".
        :param full_string: Full string, sometimes may ignore some part.
        :return: tuple[str | list, int]
        """
        return self.dict_checker(dat_info_string)(dat_info_string if full_string is None else full_string, queue_loader)

    # IDENTIFICATION SETTER SEGMENT PART. TO >>> NORMAL SEGMENT TYPE CHECKER PART.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # SETTER SEGMENT PART START.

    @staticmethod
    def int_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.INT, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def float_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.FLOAT, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def string_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.STRING, TypeExplainFormatter.DATABASE_TYPE_EXPLAIN

    @staticmethod
    def bool_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.BOOL, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def databases_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.DATABASE, TypeExplainFormatter.DATABASE_TYPE_EXPLAIN

    @staticmethod
    def file_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.FILE, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    @staticmethod
    def anything_segment_type_checker(*_) -> tuple[str, int]:
        return ConfigurationTypeKeyword.ANYTHING, TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN

    # SETTER SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SETTER SEGMENT PART. TO >>> COMPLEX SEGMENT TYPE CHECKER PART.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From those function part, is the complex type checker, which used to check the complex type and return the correct value.
    # -> Complex type is the type which need to check the inner type, like TABLE, UNION, LIST, ENUM, and CONVERSION.
    # -> So, from here, to use special function, we can check the complex type and return the correct value.
    #
    # SETTER SEGMENT PART START.

    def table_segment_type_checker(self,
                                   dat_info_string: str,
                                   queue_loader: Queue[tuple[str, int]]) -> tuple[list, int]:
        """
        This part of function is used to parse the table type.
        :param queue_loader: String saving's queue.
        :param dat_info_string: The basic string which you want to check.
        :return: tuple[type, ctypes.c_uint8]
        """
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=5
        )
        final_return_list: list[tuple[str | list, int]] = []
        table_element_type_info_string: str = dat_info_string[limit_range[0] + 1: limit_range[1]]

        # Start to parse the column of the list.
        for table_raw_column in split_top_level_string(table_element_type_info_string, ","):
            table_column_word: str = table_raw_column.strip()
            if table_column_word == "":
                continue

            # In here, we need to check the special type.
            column_type, explain_handler = self.resolve_type(table_raw_column, table_raw_column, queue_loader)
            final_return_list.append((column_type, explain_handler))

        # Ok, so finally, we can return the list.
        return final_return_list, TypeExplainFormatter.TABLE_TYPE_EXPLAIN

    def union_segment_type_checker(self,
                                   dat_info_string: str,
                                   queue_loader: Queue[tuple[str, int]]) -> tuple[list, int]:
        """
        This function will return a type value and a format signal, which means the value's type and value's format.\n
        From the UNION type, is following those rules.\n
        - Start with UNION keyword, use <> to block the detail information.\n
        - Each element in the union is separated by a comma.\n
        - The type of each element is checked individually.\n
        - Result is a list of types, and the format signal is a default type explain.\n
        - Final value's type need to be included in the list.\n
        :param queue_loader:
        :param dat_info_string: The basic string which you want to check.
        :return: tuple[type, int]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the 'dat_info_string' segment.")

        # Get the bracket's edge and push the urgent part into the new value.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=5
        )
        dat_info_string: str = dat_info_string[limit_range[0] + 1: limit_range[1]]
        final_return_list: list[tuple[str | list, int]] = []

        # Start the range and check the value's format.
        for type_list_column in split_top_level_string(dat_info_string, ","):
            type_column_word: str = type_list_column.strip()
            if type_column_word == "":
                continue
            column_types, explain = self.resolve_type(type_column_word, type_column_word, queue_loader)
            final_return_list.append((column_types, explain))

        # So finally, we can return the value's list.
        return final_return_list, TypeExplainFormatter.UNION_TYPE_EXPLAIN

    @staticmethod
    def enum_segment_type_checker(dat_info_string: str,
                                  queue_loader: Queue[tuple[str, int]]) -> tuple[list[str], int]:
        """
        This function is used to check the Enum data's type and value's format.\n
        The Enum data type is following those rules.\n
        - Start with ENUM keyword, use <> to block the detail information.\n
        - Default type is ANYTHING, ENUM is similar to: -> Limit().\n
        - Support all the data's type except DATABASE.
        :param queue_loader: A queue which saved the string value.
        :param dat_info_string: The basic string which you want to check.
        :return: tuple[list[str], ctypes.c_uint8]
        """
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=4  # len("enum") = 4
        )
        inner_string:  str       = dat_info_string[limit_range[0] + 1: limit_range[1]]
        final_saving:  list[Any] = []

        # Start to parse the data.
        for raw_value in split_top_level_string(inner_string, ","):
            temp_saving_string: str = raw_value.strip()
            if temp_saving_string == "":
                continue
            final_saving.append(scalar_value_loader(temp_saving_string, queue_loader))

        # Check the empty case.
        if len(final_saving) == 0:
            raise SyntaxError("ENUM<...> needs at least one candidate value.")
        return final_saving, TypeExplainFormatter.ENUM_TYPE_EXPLAIN

    def conversion_segment_type_checker(self,
                                        dat_info_string: str,
                                        queue_loader: Queue[tuple[str, int]]) -> tuple[str | list, int]:
        """

        :param queue_loader: The queue which saved the string.
        :param dat_info_string: The basic string which you want to convert.
        :return: tuple[str | list, ctypes.c_uint8]
        """
        if dat_info_string is None:
            raise ValueError("This function need to get the dat_info_string segment.")
        dat_info_string = dat_info_string.lower()

        # Start to check the limit range.
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=10  # len("conversion") = 10
        )
        dat_info_string: str = dat_info_string[limit_range[0] + 1: limit_range[1]]
        return_type: str | list = self.resolve_type(dat_info_string, dat_info_string, queue_loader)[0]
        return return_type, TypeExplainFormatter.DEFAULT_CONVERSION_EXPLAIN

    def list_segment_type_checker(self,
                                  dat_info_string: str,
                                  queue_loader: Queue[tuple[str, int]]) -> tuple[str | list, int]:
        """

        :param dat_info_string: Target type description's string.
        :param queue_loader: The queue which saved the string.
        :return: tuple[str | list, c_uint8]
        """
        limit_range: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=4  # len("list") = 4
        )
        inner_string: str = dat_info_string[limit_range[0] + 1: limit_range[1]]
        return_type: str | list = self.resolve_type(inner_string, inner_string, queue_loader)[0]
        return return_type, TypeExplainFormatter.LIST_TYPE_EXPLAIN

    # SETTER SEGMENT PART END.
    # endregion
