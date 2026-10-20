import copy
from typing import Any
from queue import Queue

from src.v10.struct.signal import TypeExplainFormatter, ValueFormatter
from src.v10.struct.kword import ConfigurationChangeableKeyword
from src.v10.struct.datastruct import ConfigurationDataItemStructure
from src.v10.parser.column.typechk import DatabasesSegmentTypeChecker
from src.v10.valchk.strchk.contain import split_top_level_statements_static, brackets_edge_index_checker
from src.v10.parser.column.valuechk import DatabasesSegmentValueChecker
from src.v10.parser.column.extchk import DatabaseSegmentExtensionRequireChecker
from src.v10.struct.kword import ConfigurationValueReplacerKeyword
from src.v10.struct.datastruct import ConfigurationValueStructure
from src.v10.struct.kword import ConfigurationTypeKeyword
from src.v10.valchk.strchk.splitter import split_top_level_string


class ConfigurationDatabaseStandalone(object):
    def __init__(self, data_string: str, string_memory: Queue[str]) -> None:
        if data_string.startswith("{"):
            data_string = data_string[1:]
        if data_string.endswith("}"):
            data_string = data_string[:-1]
        data_string = data_string.strip()

        # Prepare for the booting.
        self._string_memory: Queue[str] = string_memory
        self._dictionary: dict[str, ConfigurationDataItemStructure] = {}
        self._main_db_statement: list[str] = split_top_level_statements_static(data_string)

    def start_run(self) -> None:
        self.load_database_checker(self._main_db_statement, self._dictionary)

    def load_database_checker(self,
                              statement: list[str],
                              dictionary: dict[str, ConfigurationDataItemStructure]) -> None:
        """
        Loop and parse all the data in here.
        :return: None
        """
        for database_element in statement:
            element_start_pointer: int                   = 0
            element_limit_list:    list[tuple[Any, int]] = []

            # Name search.
            element_start_pointer += self._name_edge_check(database_element)
            element_name = database_element[:element_start_pointer].strip()

            # Type search.
            element_end_pointer = element_start_pointer
            element_end_pointer += self._type_edge_check(database_element[element_start_pointer:])
            element_type_name, element_type_info = self._database_check_type_segment(
                database_element[element_start_pointer: element_end_pointer].strip()
            )
            conversion_value: bool = element_type_info == TypeExplainFormatter.DEFAULT_CONVERSION_EXPLAIN
            element_type_info = TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN if conversion_value else element_type_info
            element_type: tuple[str | list, int] = element_type_name, element_type_info

            # Changeable search.
            element_end_pointer += 1
            element_start_pointer = element_end_pointer
            element_end_pointer += self._changeable_edge_check(database_element[element_start_pointer:])
            element_changeable = self._database_check_changeable_segment(database_element[element_start_pointer: element_end_pointer])

            # Value Search. In here, we need to add some little check.
            element_end_pointer += 1
            element_start_pointer = element_end_pointer
            element_value, extension_require, element_start_pointer, element_end_pointer = self._database_parse_value(
                database_element, element_type, element_start_pointer, element_end_pointer
            )

            # Extension require search.
            if extension_require:
                element_start_pointer = element_end_pointer
                element_limit_list = self._databases_check_extension_segment(database_element[element_start_pointer:].strip(), element_type)

            # Input the value.
            self._add_dictionary(
                name=element_name,
                probable_type=element_type,
                value=element_value,
                changeable=element_changeable,
                limit_list=element_limit_list,
                target_dictionary=dictionary
            )

    # IDENTIFICATION SEGMENT PART. TO >>> EDGE CHECK SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> Those function is used to check the every data part's edge.
    # -> It includes the name, type, changeable, value and extension require.
    # -> Some of them will return the index of the edge,
    # -> some of them will return the index and a bool value to indicate whether it has the edge or not.
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def _name_edge_check(string: str) -> int:
        return string.find("[")

    @staticmethod
    def _type_edge_check(string: str) -> int:
        return brackets_edge_index_checker(string, 0, "[", "]")[1]

    @staticmethod
    def _changeable_edge_check(string: str) -> int:
        return string.find("=")

    @staticmethod
    def _normal_value_edge_check(string: str) -> tuple[int, bool]:
        """
        Check normal static value part's edge.
        :param string: Target data string's part.
        :return: tuple[int, bool]
        """
        scan_index: int = 0

        # Search the legal '->' end signal.
        while scan_index < len(string) - 1:
            scan_char: str = string[scan_index]
            if scan_char == "-" and string[scan_index + 1] == ">":
                return scan_index + 2, True  # The value stops right before '->'.
            scan_index += 1

        # Never find the end signal, means don't have any extension require.
        return -1, False

    @staticmethod
    def _databases_segment_edge_check(value_string_part: str) -> tuple[int, int]:
        inner_brace_idx: int = value_string_part.find("{")
        return brackets_edge_index_checker(value_string_part, inner_brace_idx, "{", "}")

    @staticmethod
    def _table_segment_edge_checker(value_string_part: str) -> tuple[int, int]:
        inner_brace_idx: int = value_string_part.find("[")
        return brackets_edge_index_checker(value_string_part, inner_brace_idx, "[", "]")

    @staticmethod
    def _list_segment_edge_checker(value_string_part: str) -> tuple[int, int]:
        inner_brace_idx: int = value_string_part.find("[")
        return brackets_edge_index_checker(value_string_part, inner_brace_idx, "[", "]")

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >> DB PART CHECK SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _database_check_type_segment(self, type_element: str) -> tuple[str | list | Any, int]:
        if type_element.startswith("["): type_element = type_element[1:]    # noqa
        if type_element.endswith("]"): type_element = type_element[:-1]     # noqa

        # Check and return the data's type realize string.
        type_checker: DatabasesSegmentTypeChecker = DatabasesSegmentTypeChecker()
        sub_index: int = type_element.find("<")
        type_word: str = type_element.strip() if sub_index == -1 else type_element[:sub_index].strip()
        return_segment: tuple[str | list | Any, int] = type_checker.dict_checker(type_word)(type_element, self._string_memory)
        return return_segment

    @staticmethod
    def _database_check_changeable_segment(changeable_segment: str) -> bool:
        match changeable_segment.strip():
            case ConfigurationChangeableKeyword.CONSTANT: return False
            case ConfigurationChangeableKeyword.MUTABLE:  return True   # noqa
            case _: raise TypeError(f"Unknown type {changeable_segment}.")

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> TABLE APPLY SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> Those function is used to parse table segment.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _database_apply_table(self, load_data_string: str, table_type: list[tuple[str | list, int]]) -> list:
        """
        Load one `[...]` table literal into a list of rows.
        Two shapes are legal, exactly as Grammar.bnf describes them:
            [TABLE<INT, STR>] = [(1, "a"), (2, "b")]             -> parenthesized rows\n
        Each returned row is a plain list holding one value per column, so the whole table always
        follows the declared signature. It used to return half-built segment structures, drop
        every nested row and blow up with IndexError as soon as there were more elements than
        declared columns.
        :return:
        """
        if load_data_string.strip() == "":
            return []
        final_return_list: list = []

        # Check the item in the table.
        for table_cell_statement in split_top_level_string(load_data_string):
            table_cell_statement = table_cell_statement.strip()
            table_cell_statement = table_cell_statement[1:]
            table_cell_statement = table_cell_statement[:-1]
            table_cell_statement = table_cell_statement.strip()

            # Split the value, and get the child statement.
            table_cell_statement = split_top_level_string(table_cell_statement)
            table_cell_list: list[ConfigurationValueStructure] = []
            for table_index, table_cell_item in enumerate(table_cell_statement):
                value_structure: ConfigurationValueStructure = ConfigurationValueStructure()
                value_structure.value = self._database_parse_value(table_cell_item, table_type[table_index], 0, 0)[0]
                table_cell_list.append(value_structure)
            final_return_list.append(tuple(table_cell_list))

        return final_return_list

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> VALUE APPLY SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _database_apply_normal_value(self, value_string: str, probable_type: str) -> list[tuple[Any, int]]:
        """

        :param value_string:
        :param probable_type:
        :return:
        """
        value_checker: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker()
        parsing_function: Any = value_checker.auto_check(probable_type)
        return_string: list[tuple[Any, int]] = parsing_function(value_string, self._string_memory)
        return return_string

    def _database_parse_value(self,
                              database_element:      str,
                              element_type:          tuple[str | list, int],
                              element_start_pointer: int,
                              element_end_pointer:   int) -> tuple[list[tuple[Any, int]], bool, int, int]:
        """

        :param database_element: All the element of the data sentence.
        :param element_type: Data's type, realized by type checker.
        :param element_start_pointer: Until now, the pointer of start.
        :param element_end_pointer: Until now, the pointer of end.
        :return:
        """
        element_value:     list[tuple[Any, int]] = []
        extension_require: bool                  = False

        # 1. Check the database.
        if element_type[1] == TypeExplainFormatter.DATABASE_TYPE_EXPLAIN:
            load_dictionary: dict[str, ConfigurationDataItemStructure] = {}
            try:
                element_start_pointer, element_end_pointer = self._databases_segment_edge_check(database_element[element_start_pointer])
                extension_require = self._normal_value_edge_check(database_element[element_end_pointer:])[1]
                child_statement: list[str] = split_top_level_statements_static(database_element.strip()[1:])
                self.load_database_checker(child_statement, load_dictionary)
                element_value = [(load_dictionary, ValueFormatter.DATABASE_FORMATTER)]
            except IndexError:
                element_value = [(ConfigurationValueReplacerKeyword.NULL, ValueFormatter.KEYWORD_SIGNAL_FORMATTER)]

        # 2. Check the table type.
        elif element_type[1] == TypeExplainFormatter.TABLE_TYPE_EXPLAIN:
            try:
                element_start_pointer, element_end_pointer = self._table_segment_edge_checker(database_element[element_end_pointer])
                extension_require = self._normal_value_edge_check(database_element[element_end_pointer])[1]
                table_list: list[ConfigurationValueStructure] = self._database_apply_table(
                    database_element[element_start_pointer + 1: element_end_pointer],
                    element_type[0]     # noqa
                )
                element_value = [(table_list, ValueFormatter.TABLE_FORMATTER)]
            except IndexError:
                element_value = [(ConfigurationValueReplacerKeyword.NULL, ValueFormatter.KEYWORD_SIGNAL_FORMATTER)]

        # 3. Check the list type.
        elif element_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
            try:
                element_start_pointer, element_end_pointer = self._table_segment_edge_checker(database_element[element_end_pointer])
                extension_require = self._normal_value_edge_check(database_element[element_end_pointer])[1]
            except IndexError:
                element_value = [(ConfigurationValueReplacerKeyword.NULL, ValueFormatter.KEYWORD_SIGNAL_FORMATTER)]

        # 4. Check the enum type.
        elif element_type[1] == TypeExplainFormatter.ENUM_TYPE_EXPLAIN:
            value_segment_info, extension_require = self._normal_value_edge_check(database_element[element_end_pointer:])
            element_end_pointer += value_segment_info if extension_require else len(database_element[element_end_pointer:])
            element_value = self._database_apply_normal_value(
                database_element[element_start_pointer: element_end_pointer - 2 if extension_require else 0],
                ConfigurationTypeKeyword.ANYTHING
            )

        # Other: Load with normal type.
        elif element_type[1] == TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN:
            value_segment_info, extension_require = self._normal_value_edge_check(database_element[element_start_pointer:])
            element_end_pointer += value_segment_info if extension_require else len(database_element[element_start_pointer:])
            element_value = self._database_apply_normal_value(
                database_element[element_start_pointer: element_end_pointer - 2 if extension_require else 0],
                element_type[0]     # noqa
            )

        # We may get some unknown error, so put an exception in here.
        else:
            raise NotImplementedError(element_type)

        # Return the value and signal information for the next part.
        return element_value, extension_require, element_start_pointer, element_end_pointer

    def _databases_check_extension_segment(self, extension_segment: str, value_type: tuple[str | list[Any], int]) -> list[tuple[Any, int]]:
        final_list: list[tuple[Any, int]] = []
        extension_checker: DatabaseSegmentExtensionRequireChecker = DatabaseSegmentExtensionRequireChecker()
        extension_segment_list: list[str] = split_top_level_statements_static(extension_segment)
        for segment_item in extension_segment_list:
            return_function: Any = extension_checker.auto_return(segment_item)
            blank_left, blank_right = brackets_edge_index_checker(
                dat_info_string=segment_item,
                right_move=0,
                left_bracket="(",
                right_bracket=")"
            )
            segment_item = segment_item[blank_left + 1: blank_right]
            final_list.append(return_function(segment_item, value_type, self._string_memory))
        return final_list

    # CODE SEGMENT PART END.
    # endregion

    @staticmethod
    def _add_dictionary(name:              str,
                        probable_type:     tuple[str | list | Any, int],
                        value:             list[tuple[Any, int]],
                        changeable:        bool,
                        limit_list:        list[tuple[Any, int]],
                        target_dictionary: dict[str, ConfigurationDataItemStructure]) -> None:
        """

        :param name: The name (or key) of the data.
        :param probable_type: Which type it can contain.
        :param value: All the value of the name.
        :param changeable: It can be changed or not.
        :param limit_list: The value it limited.
        :param target_dictionary: Where to input the value.
        :return:
        """
        structure: ConfigurationDataItemStructure = ConfigurationDataItemStructure()
        structure.probable_type = copy.deepcopy(probable_type)
        structure.value         = copy.deepcopy(value)
        structure.changeable    = copy.deepcopy(changeable)
        structure.limit_list    = copy.deepcopy(limit_list)
        target_dictionary[name] = structure

    @property
    def get_final_dictionary(self) -> dict[str, ConfigurationDataItemStructure]:
        return self._dictionary
