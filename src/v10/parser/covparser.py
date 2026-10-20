from queue import Queue

from src.v10.valchk.strchk.contain import split_top_level_statements_static
from src.v10.struct.datastruct import ConfigurationConversionStructure


class ConfigurationConversionStandalone(object):
    def __init__(self,
                 data_string: str,
                 string_saving_queue: Queue[tuple[str, int]]) -> None:
        self._data_string: list[str] = split_top_level_statements_static(data_string)
        self._string_saving_queue: Queue[tuple[str, int]] = string_saving_queue
        self._directory: dict[str, ConfigurationConversionStructure] = {}

    def start_run(self) -> None:
        ...

    @property
    def get_final_dictionary(self) -> dict[str, ConfigurationConversionStructure]:
        return self._directory
