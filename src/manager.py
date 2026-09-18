import dataclasses
import uuid
import os
from queue import Queue
from typing import Any

from queue import Queue
from typing import Any

from src.parsefunc.function import isinstance_loose
from src.parseutil.structure import ConfigurationDataStandaloneSegmentStructure
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

        # CRITICAL: the traversal must be guarded against revisiting a value it already walked.
        # The previous version pushed the item it had just popped straight back into the same
        # queue whenever the shape was not recognised, which is an endless loop, and a node
        # reachable from several parents was visited over and over again too.
        visited: set[int] = set()

        def enqueue(target: Any) -> None:
            """
            Register one node for the breadth first walk.

            :param target: Any    Structure whose `.value` may hold nested children.
            :return: None
            """
            if target is None or id(target) in visited:
                return
            visited.add(id(target))
            queue_loader.put(target)

        def explore_container(container: Any) -> None:
            """
            Push every nested dictionary / list reachable from `container` into the walk.

            :param container: Any    Value coming from a segment.
            :return: None
            """
            stack: list[Any] = [container]
            while stack:
                item: Any = stack.pop()

                if isinstance_loose(item, ConfigurationDataStandaloneSegmentStructure):
                    enqueue(item)
                    continue

                if isinstance_loose(item, dict):
                    enqueue(item)
                    continue

                if isinstance_loose(item, list) or isinstance_loose(item, tuple):
                    # A plain list/tuple is only walked; it never goes back into the BFS with the
                    # same identity twice, so the walk always terminates.
                    if id(item) in visited:
                        continue
                    visited.add(id(item))
                    stack.extend(item)

        # Push the first level's value into the searching queue.
        for structure_item in self._origin_list:
            for configuration_key, configuration_value in structure_item.structure_pointer.dictionary.items():
                if configuration_key in args:
                    final_saving_list.append(configuration_value)
                    continue

                enqueue(configuration_value)

        # Start the loop and check the value in here.
        while not queue_loader.empty():
            queue_loader_item: Any = queue_loader.get()

            # Start to search it. Unwrap structures first, then DB-like dictionaries, so a node
            # reached from anywhere (top level, nested database, table row) is handled the same.
            if isinstance_loose(queue_loader_item, ConfigurationDataStandaloneSegmentStructure):
                try:
                    queue_loader_item = queue_loader_item.value
                except Exception:  # noqa: BLE001  - a broken value must not kill the search.
                    continue

            if isinstance_loose(queue_loader_item, dict):
                children: Any = queue_loader_item.items()
            else:
                children = ((None, queue_loader_item),)

            for configuration_key, configuration_value in children:
                if configuration_key is not None and configuration_key in args:
                    final_saving_list.append(configuration_value)
                    continue

                explore_container(configuration_value)

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

