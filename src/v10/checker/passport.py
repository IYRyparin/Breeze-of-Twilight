from src.v10.struct.datastruct import ConfigurationDataItemStructure


class ValueTypeCheck(object):
    def __init___(self, segment_structure: ConfigurationDataItemStructure) -> None:
        self._segment_structure = segment_structure

    def _normal_item_value_check(self) -> bool:
        ...

