import uuid

from v10.struct.datastruct import ConfigurationDataItemStructure


class FileOriginStructure(object):
    # +---------------+------------------------------------------+-------------------+-----------------+
    # |      NAME     |                   TYPE                   |        VALUE      |      EXPLAIN    |
    # +---------------+------------------------------------------+-------------------+-----------------+
    structure_uuid:    str                                       = str(uuid.uuid4())  # Unique id, realize by manager.
    from_filepath:     str                                       = "N/A"              # Read from which file.
    config_id:         str                                       = "N/A"              # Config's realize id.
    config_version:    float                                = 0.0                # Which version it follows.
    config_encode:     str                                       = "utf-8"            # Which encode it used.
    config_readonly:   bool                                      = False              # Frozen readonly lock.
    structure_pointer: dict[str, ConfigurationDataItemStructure] = None               # Structure's pointer.
    # +---------------+------------------------------------------+-------------------+-----------------+
