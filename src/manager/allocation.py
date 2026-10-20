import os
import importlib
from queue import Queue
from typing import Any

from src.v10.parser.column.valuechk import DatabasesSegmentValueChecker
from src.v10.root.decimal import ConversionDecimal
from src.v10.struct.kword import ConfigurationDefineKeyword
from src.v10.valchk.strchk.strtake import take_saved_string, load_string_saving_queue
from src.v10.struct.datastruct import ConfigNodeHeaderStructure
from src.v10.valchk.strchk.contain import split_top_level_statements_static


class ConfigIdentifyLoader(object):
    CONFIGURATION_ID: str = ""
    CONFIGURATION_VERSION: float = 0.0
    CONFIGURATION_READONLY: bool = False
    CONFIGURATION_ENCODE: str = "utf-8"
    STRUCTURE_INDEX: tuple[int, int, int, int] = (-1, -1, -1, -1)

    def __init__(self, config_filepath: str, encoding: str = "utf-8") -> None:
        with open(config_filepath, "r", encoding=encoding) as config_file:  # When we don't know the encoding, we can try to load it as utf-8.
            self._config_string: str = config_file.read()
        config_file.close()

        # Load the string saving queue and the basic string value.
        self._string_saving_queue, self._basic_string = load_string_saving_queue(self._config_string)
        self._basic_string = self._basic_string.replace("\n", "")
        self._temp_string_split_chain: list[str] = split_top_level_statements_static(self._basic_string)  # Identify keyword don't care about any value, so we can break it.
        self.STRUCTURE_INDEX = self._segment_signal_searcher(self._temp_string_split_chain)
        pass

    def _segment_signal_searcher(self, string_chain: list[str]) -> tuple[int, int, int, int]:
        database_start_index:   int = -1
        database_end_index:     int = -1
        conversion_start_index: int = -1
        conversion_end_index:   int = -1

        # Start the loop to check the value's part's start and end segment.
        for segment_index, string_segment_item in enumerate(string_chain):
            if string_segment_item.strip() == "":
                continue

            # Check the string's segment in here.
            match string_segment_item.strip().split()[0]:
                case ConfigurationDefineKeyword.DATABASES_START:
                    database_start_index = segment_index
                case ConfigurationDefineKeyword.DATABASES_END:
                    database_end_index = segment_index
                case ConfigurationDefineKeyword.CONVERSION_START:
                    conversion_start_index = segment_index
                case ConfigurationDefineKeyword.CONVERSION_END:
                    conversion_end_index = segment_index
                case ConfigurationDefineKeyword.IDENTIFICATION:
                    self._load_identification_title(string_segment_item)

        # Push out the correct part in here.
        return database_start_index, database_end_index, conversion_start_index, conversion_end_index

    # IDENTIFICATION SEGMENT PART. TO >>> LOAD IDENTIFICATION SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _load_identification_title(self, title_element: str) -> None:
        """
        This function is used to load the title.
        Only used in the standalone mode, because the title is not needed in the database mode.
        :param title_element: str   The title element which will be loaded.
        :return: None
        """
        title_element: str = title_element.strip()
        if title_element == "":
            return

        # Start to check the segment, input the useful part into the structure.
        title_configuration_describe, title_configuration_value = list(filter(lambda n: n != "", title_element.split(" ")[1: 3]))
        match title_configuration_describe:
            case ConfigurationDefineKeyword.CONFIGURE_ID:  # Load configuration id, get the id's string from string's memory.
                self.CONFIGURATION_ID = take_saved_string(self._string_saving_queue)[0]
            case ConfigurationDefineKeyword.CONFIGURE_VERSION:  # Load configuration version into the value.
                self.CONFIGURATION_VERSION = float(ConversionDecimal(title_configuration_value).auto_changer())
            case ConfigurationDefineKeyword.CONFIGURE_READONLY:  # Load configuration's readonly info into the value.
                self.CONFIGURATION_READONLY = DatabasesSegmentValueChecker.boolean_parser(title_configuration_value, None)[0][0]
            case ConfigurationDefineKeyword.CONFIGURE_ENCODE:  # Load configurations encode info into the value.
                self.CONFIGURATION_ENCODE = take_saved_string(self._string_saving_queue)[0]
            case _:
                raise ValueError(f"Unknown configuration {title_configuration_value}.")

    # CODE SEGMENT PART END.
    # endregion
    @property
    def basic_string(self):
        return self._basic_string

    @property
    def string_saving_queue(self):
        return self._string_saving_queue

    @property
    def temp_string_split_chain(self):
        return self._temp_string_split_chain


def move_search_parser(version: float) -> str:
    """
    Change the parser to the correct version.
    :return: str
    """
    version: str = str(version)
    direct_item: str = "v10"
    for direct_item in list(filter(lambda n: n.startswith("v"), os.listdir("./src/"))):
        if version[0] + version[2] == direct_item[1:]:
            return direct_item
    return direct_item


class ConfigAllocation(object):
    def __init__(self, config_filepath: str) -> None:
        self._allocation: ConfigIdentifyLoader = ConfigIdentifyLoader(config_filepath)
        if self._allocation.CONFIGURATION_ENCODE != "utf-8":  # Not the default encode, reload the file.
            self._allocation = ConfigIdentifyLoader(config_filepath, self._allocation.CONFIGURATION_ENCODE)
        parser_direct: str = move_search_parser(self._allocation.CONFIGURATION_VERSION)
        self._module: Any = importlib.import_module(f"src.{parser_direct}.parser.dbparser")
        self._cov_module: Any = importlib.import_module(f"src.{parser_direct}.parser.covparser")

        # Push the node header into the structure
        self._header = ConfigNodeHeaderStructure()
        self._header.CONFIGURATION_ID = self._allocation.CONFIGURATION_ID
        self._header.CONFIGURATION_VERSION = self._allocation.CONFIGURATION_VERSION
        self._header.CONFIGURATION_ENCODE = self._allocation.CONFIGURATION_ENCODE
        self._header.CONFIGURATION_READONLY = self._allocation.CONFIGURATION_READONLY
        self._header.config_filepath = config_filepath

    def get_division_string(self) -> tuple[str, str]:
        structure_index: tuple[int, int, int, int] = self._allocation.STRUCTURE_INDEX
        allocation_split_chain: list[str] = self._allocation.temp_string_split_chain
        database_part: list[str] = []
        conversion_part: list[str] = []
        if structure_index[0] != -1 and structure_index[1] != -1:
            database_part = allocation_split_chain[structure_index[0] + 1: structure_index[1]]
        if structure_index[2] != -1 and structure_index[3] != -1:
            conversion_part = allocation_split_chain[structure_index[2] + 1: structure_index[3]]
        return ";".join(database_part), ";".join(conversion_part)

    def get_node_header(self) -> ConfigNodeHeaderStructure:
        return self._header

    def get_string_saving_queue(self) -> Queue[tuple[str, int]]:
        return self._allocation.string_saving_queue

    def get_correct_database_module(self) -> Any:
        return self._module

    def get_correct_conversion_module(self) -> Any:
        return self._cov_module
