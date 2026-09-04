import dataclasses
import uuid
import os
from queue import Queue
from typing import Any

from parsefunc.function import isinstance_loose
from parseutil.structure import ConfigurationDataStandaloneSegmentStructure
from src.parsecheck.logs import LogCatalogue, EmptyLogCatalogue
from src.parser import ConfigurationStandalone


# ----- SOURCE START -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> CONFIGURATION MANAGER CLASS.
#
# region
# INTRODUCE SENTENCE.
# -> From here, is the configuration file manager's source code.
# -> How it works?
#
# CODE SEGMENT START.


@dataclasses.dataclass
class FileOriginStructure(object):
    # +---------------+------------------------+-------------------+-----------------+
    # |      NAME     |           TYPE         |        VALUE      |      EXPLAIN    |
    # +---------------+------------------------+-------------------+-----------------+
    structure_pointer: ConfigurationStandalone
    from_filepath:     str                     = "N/A"
    structure_id:      str                     = str(uuid.uuid4())
    # +---------------+------------------------+-------------------+-----------------+


class ConfigurationManager(object):
    def __init__(self, logging_mode: bool = False) -> None:
        self._logview:     Any                            = LogCatalogue() if logging_mode else EmptyLogCatalogue()
        self._origin_list: list[FileOriginStructure]      = []
        self._master:      ConfigurationStandalone | None = None

    # IDENTIFICATION SEGMENT PART. TO >>> CONFIG LOADER SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def load_file(self, filepath: str) -> None:
        """

        :param filepath: str
        :return: None
        """
        if not os.path.isfile(filepath) or not os.access(filepath, os.R_OK):
            raise FileNotFoundError(f"{filepath} is not a file or not allowed.")

        # Start to load the file.
        with open(filepath, "r") as origin_file:
            data_struct: ConfigurationStandalone = ConfigurationStandalone(origin_file.read())
            file_struct: FileOriginStructure     = FileOriginStructure(data_struct)

            # Initialize the value.
            file_struct.from_filepath = filepath

            # Push the structure into the list.
            self._origin_list.append(file_struct)

        # Finally, close the file.
        origin_file.close()

    def load_data(self, data: str) -> None:
        """

        :param data:
        :return:
        """
        data_struct: ConfigurationStandalone = ConfigurationStandalone(data)
        file_struct: FileOriginStructure = FileOriginStructure(data_struct)

        # Push the structure into the list.
        self._origin_list.append(file_struct)

    def save_file(self) -> None:
        ...  # TODO: Fix the file saving mode.

    def save_data(self, link: int) -> str:
        ...  # TODO: Fix the data saving mode.

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> ID SETTER.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def master_point_uuid(self, point: str) -> bool:
        """

        :param point:
        :return:
        """
        for structure_item in self._origin_list:
            if structure_item.structure_id == point:
                self._master = structure_item.structure_pointer
                return True
        return False

    def master_point_identification_id(self, point: str) -> bool:
        """

        :param point:
        :return:
        """
        for structure_item in self._origin_list:
            if structure_item.structure_pointer.CONFIGURATION_ID == point:
                self._master = structure_item.structure_pointer
                return True
        return False

    def master_point_origin_path(self, point: str) -> bool:
        """

        :param point:
        :return:
        """
        for structure_item in self._origin_list:
            if structure_item.from_filepath == point:
                self._master = structure_item.structure_pointer
                return True
        return False

    def master_point_list_index(self, point: int) -> bool:
        """

        :param point:
        :return:
        """
        try:
            self._master = self._origin_list[point].structure_pointer
            return True
        except IndexError:
            return False

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> SEARCH SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def search(self, *args) -> list[ConfigurationDataStandaloneSegmentStructure]:
        """

        :param args: ...
        :return: list[ConfigurationDataStandaloneSegmentStructure]
        """
        final_saving_list: list[ConfigurationDataStandaloneSegmentStructure] = []

        # Start to initialize some value in here, prepare for the search.
        queue_loader: Queue = Queue()
        temp_queue:   Queue = Queue()

        # Push the first level's value into the searching queue.
        for structure_item in self._origin_list:
            for configuration_key, configuration_value in structure_item.structure_pointer.dictionary.items():
                if configuration_key in args:
                    final_saving_list.append(configuration_value)

                # Check and load the special type in here, load it into the queue.
                elif isinstance_loose(configuration_value.value, dict):
                    queue_loader.put(configuration_value)

                # Check the changeable list.
                elif isinstance_loose(configuration_value.value, list):
                    temp_queue.put(configuration_value)

                    # Start the list's range.
                    while not temp_queue.empty():
                        temp_item: list[Any] = temp_queue.get()

                        # Check the data in list, push the list into the queue.
                        if isinstance_loose(temp_item, list):
                            temp_queue.put(temp_item)

                        # Or anything else, push the dict into the queue.
                        elif isinstance_loose(temp_item, dict):
                            queue_loader.put(temp_item)

        # Start the loop and check the value in here.
        while not queue_loader.empty():
            queue_loader_structure: ConfigurationDataStandaloneSegmentStructure = queue_loader.get()

            # Start to search it.
            for configuration_key, configuration_value in queue_loader_structure.value.items():
                if configuration_key in args:
                    final_saving_list.append(configuration_value)

                # Check and load the special type in here, load it into the queue.
                elif isinstance_loose(configuration_value.value, dict):
                    queue_loader.put(configuration_value)

                # Check the changeable list.
                elif isinstance_loose(configuration_value.value, list):
                    temp_queue.put(configuration_value)

                    # Start the list's range.
                    while not temp_queue.empty():
                        temp_item: list[Any] = temp_queue.get()

                        # Check the data in list, push the list into the queue.
                        if isinstance_loose(temp_item, list):
                            temp_queue.put(temp_item)

                        # Or anything else, push the dict into the queue.
                        elif isinstance_loose(temp_item, dict):
                            queue_loader.put(temp_item)

        # Finally, just return the list.
        return final_saving_list

    # CODE SEGMENT PART END.
    # endregion

    def __getitem__(self, item: str) -> ConfigurationDataStandaloneSegmentStructure:
        if self._master is not None:
            return self._master.dictionary[item.lower()]  # noqa
        raise KeyError(item)


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----

