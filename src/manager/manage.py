import pprint
from uuid import uuid4
from typing import Any
from queue import Queue

from src.manager.allocation import ConfigAllocation
from src.v10.struct.datastruct import ConfigurationDataItemStructure, ConfigurationConversionStructure, ConfigNodeHeaderStructure
from src.v10.struct.signal import TypeExplainFormatter, ValueFormatter


class ConfigManager:
    def __init__(self) -> None:
        self.__manage_allocation: dict[str, ConfigNodeHeaderStructure] = {}
        self.__manage_database: dict[str, dict[str, ConfigurationDataItemStructure]] = {}
        self.__manage_conversion: dict[str, ConfigurationConversionStructure] = {}
        self.__pointer: str = ""
        self.__direction: list[str] = []

    # IDENTIFICATION SEGMENT PART. TO >>> CONFIG OPERATOR SEGMENT.
    #
    # region
    # INTRODUCE SEGMENT.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT START.

    def printer(self) -> None:
        p = pprint.PrettyPrinter(indent=4)
        p.pprint(self.__manage_allocation)
        p.pprint(self.__manage_database)
        p.pprint(self.__manage_conversion)
        p.pprint(self.__pointer)
        p.pprint(self.__direction)

    def load_file(self,
                  filepath: str,
                  master_pointer: bool = False) -> None:
        """

        :param filepath:
        :param master_pointer:
        :return: None
        """
        one_uid: str = uuid4().hex
        allocation: ConfigAllocation = ConfigAllocation(filepath)
        string_saving_queue: Queue[tuple[str, int]] = allocation.get_string_saving_queue()
        database_part, conversion_part = allocation.get_division_string()
        allocation_structure: ConfigNodeHeaderStructure = allocation.get_node_header()
        self.__manage_allocation[one_uid] = allocation_structure
        module: Any = allocation.get_correct_database_module()

        # Start to parse the database part.
        database_parser: Any = module.ConfigurationDatabaseStandalone(database_part, string_saving_queue)
        database_parser.start_run()
        self.__manage_database[one_uid] = database_parser.get_final_dictionary

        # Load the conversion part.
        module: Any = allocation.get_correct_conversion_module()
        conversion_parser: Any = module.ConfigurationConversionStandalone(conversion_part, string_saving_queue)
        conversion_parser.start_run()
        self.__manage_conversion[one_uid] = conversion_parser.get_final_dictionary

        # Point to this new item.
        if master_pointer:
            self.__pointer = one_uid

    def load_data(self) -> None:    # TODO: Fix the raw data loader.
        ...

    def save_file(self) -> None:    # TODO: Fix the file saver.
        ...

    def save_data(self) -> str:     # TODO: Fix the raw data saver.
        ...

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> DATA CHECK SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _merge_final_value(self, value: list[tuple[Any, int]]) -> tuple[Any, int]:
        ...

    def _check_direction_correctness(self, direction: list[str]) -> bool:
        """

        :param direction: Where you want to check the direction.
        :return: bool
        """
        direction_pointer: int = 0
        segment_structure = self.__manage_database[self.__pointer]
        while len(direction) != 0:
            direction_name: str = direction[direction_pointer]
            segment_structure = segment_structure[direction_name]
            merge_final_value = self._merge_final_value(segment_structure.value)
            if (
                segment_structure.probable_type[1] == TypeExplainFormatter.DATABASE_TYPE_EXPLAIN and    # noqa
                merge_final_value[1] == ValueFormatter.DATABASE_FORMATTER
            ):
                segment_structure = segment_structure.value
                direction_pointer += 1
            elif direction_pointer == len(direction) - 1:
                return True
            else:
                return False
        return False

    def cd(self, name: str) -> bool:
        if self._check_direction_correctness([*self.__direction, name]):
            self.__direction.append(name)
            return True
        else:
            return False

    def back(self) -> bool:
        if len(self.__direction) == 0:
            return False
        self.__direction.pop()
        return True

    def get_direction(self) -> tuple[list[str], bool]:
        return self.__direction, True

    def set_direction(self, directory: str | list[str], split_char: str = ".") -> bool:
        if isinstance(directory, str):
            directory: list[str] = directory.split(split_char)
        if self._check_direction_correctness(directory):
            self.__direction = directory
            return True
        else:
            return False

    def get_item(self, name: str, pointer: str | None = None) -> tuple[Any, bool]:
        target_pointer: str = self.__pointer if pointer is None else pointer
        segment_structure: dict[str, ConfigurationDataItemStructure] = self.__manage_database[target_pointer]
        if name in segment_structure.keys():
            return segment_structure[name], True
        else:
            return None, False

    def set_item(self, name: str, value: Any) -> bool:
        ...

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> DATA SEARCH SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def master_pointer_uuid(self, uuid: str) -> bool:
        if uuid in self.__manage_database.keys():
            self.__pointer = uuid
            return True
        else:
            return False

    def master_pointer_id(self, config_id: str) -> bool:
        for key, value in self.__manage_allocation.items():
            if value.CONFIGURATION_ID == config_id.strip().lower():
                self.__pointer = key
                return True
        return False

    def master_pointer_filepath(self, filepath: str) -> bool:
        for key, value in self.__manage_allocation.items():
            if value.config_filepath == filepath.strip():
                self.__pointer = key
                return True
        return False

    def search_database_item(self, name: str) -> list[tuple[Any, int]]:
        final_search_result: list[tuple[Any, int]] = []
        queue_loader: Queue[dict[str, ConfigurationDataItemStructure]] = Queue()
        for configuration_structure in self.__manage_database.values():
            queue_loader.put(configuration_structure)

        # Start to check the correct value in the dictionary.
        while not queue_loader.empty():
            database_item: dict[str, ConfigurationDataItemStructure] = queue_loader.get()
            for data_key, data_value in database_item.items():
                final_value_merge: tuple[Any, int] = self._merge_final_value(data_value.value)
                if data_key == name:
                    final_search_result.append(final_value_merge)
                elif (
                    data_value.probable_type[1] == TypeExplainFormatter.DATABASE_TYPE_EXPLAIN and
                    self._merge_final_value(data_value.value)[1] == ValueFormatter.DATABASE_FORMATTER
                ):
                    queue_loader.put(final_value_merge[0])

        return final_search_result
