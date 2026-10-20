from queue import Queue
from typing import Any

from src.v10.parser.column.valuechk import DatabasesSegmentValueChecker
from src.v10.struct.kword import ConfigurationExtensionKeyword
from src.v10.valchk.strchk.contain import brackets_edge_index_checker
from src.v10.struct.kword import ConfigurationValueRequireSentencesKeyword
from src.v10.struct.signal import ExtensionExplainFormatter
from src.v10.valchk.strchk.splitter import split_top_level_string
from src.v10.valchk.strchk.strtake import take_saved_string


class DatabaseSegmentExtensionRequireChecker(object):
    def __init__(self) -> None:
        self._value_parser_heap: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker()

    def auto_return(self, dat_info_string: str) -> Any:
        """

        :param dat_info_string: str
        :return: Any
        """
        dat_info_string = dat_info_string.lower().strip()

        # Find the edge, defines at '(' and ')'.
        bracket: tuple[int, int] = brackets_edge_index_checker(
            dat_info_string=dat_info_string,
            right_move=0,
            left_bracket="(",
            right_bracket=")",
        )
        explain_signal: str = dat_info_string[: bracket[0]]

        # Match and return the signal.
        match explain_signal:
            case ConfigurationExtensionKeyword.LIMIT:   return self.limit_rule_explain            # noqa
            case ConfigurationExtensionKeyword.REGULAR: return self.regular_rule_explain
            case _: raise TypeError("Unknown explain type.")

    def limit_rule_explain(self,
                           dat_info_string: str,
                           value_type: tuple[str | list[Any], int],
                           string_saving_memory: Queue[str]) -> list[tuple[Any, int]]:
        """

        :param dat_info_string: The basic string which you want to check.
        :param value_type: Limited value's type.
        :param string_saving_memory: The string saving memory, you can see it's described in parser.py.
        :return: list[tuple[Any, int]]
        """
        final_return_list: list[tuple[Any, int]] = []

        # Start the loop, check the value item.
        for explain_raw_item in split_top_level_string(dat_info_string, ","):
            explain_raw_item: str = explain_raw_item.strip()
            if explain_raw_item == "":
                continue

            # Start to check the value's prefix keyword.
            temp_string_memory: str = ""
            explain: int = ExtensionExplainFormatter.LIMIT_WITHIN_VALUE
            explain_blank: list[str] = explain_raw_item.split(None, 1)
            match explain_blank[0].strip():
                case ConfigurationValueRequireSentencesKeyword.EXCLUDE:
                    temp_string_memory = explain_blank[1].rstrip()
                    explain = ExtensionExplainFormatter.LIMIT_WITHOUT_VALUE
                case _:
                    temp_string_memory = explain_blank[0]

            # Start to parse the value.
            return_function: Any = self._value_parser_heap.auto_check(value_type[0])
            get_value: list[tuple[Any, int]] = return_function(temp_string_memory, string_saving_memory)
            final_return_list.append((get_value, explain))

        return final_return_list

    @staticmethod
    def regular_rule_explain(dat_info_string: str, string_saving_memory: Queue[tuple[str, int]]) -> list[tuple[str, int]]:
        """

        :param string_saving_memory:
        :param dat_info_string:
        :return: list[tuple[Any, int]]
        """
        dat_info_string:   str                   = dat_info_string.strip()
        final_saving_list: list[tuple[Any, int]] = []

        # One entry per pattern; '!' in front of it flips the rule into "must NOT match".
        for raw_item in split_top_level_string(dat_info_string, ","):
            string_loader: str = raw_item.strip()
            if string_loader == "":
                continue

            regular_signal: int = ExtensionExplainFormatter.LIMIT_WITHIN_STRING_REGULAR

            # Search the prefix. Both '!' ("!"^bad$") and the EXCLUDE keyword are accepted; the
            # original scan only advanced the pointer on '"' so anything else spun here forever.
            while True:
                if string_loader.startswith("!"):
                    regular_signal = ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR
                    string_loader = string_loader[1:].strip()
                    continue

                lowered = string_loader.lower()
                if lowered.startswith(ConfigurationValueRequireSentencesKeyword.EXCLUDE):
                    regular_signal = ExtensionExplainFormatter.LIMIT_WITHOUT_STRING_REGULAR
                    string_loader = string_loader[7:].strip()
                    continue

                break

            # Load regular string from queue. In here, data string just used to check the prefix and count of the string.
            if string_loader.startswith('"'):
                string_loader = take_saved_string(string_saving_memory)[0]

            elif string_loader.endswith('"'):  # tolerate a stray closing quote
                string_loader = string_loader[:-1]

            if string_loader == "":
                raise SyntaxError("REGULAR(...) got an empty pattern.")

            final_saving_list.append((string_loader, regular_signal))

        if len(final_saving_list) == 0:
            raise SyntaxError("REGULAR(...) needs at least one pattern.")

        # Finally, return the list.
        return final_saving_list
