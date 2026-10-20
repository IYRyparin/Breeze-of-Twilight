from typing import Any


def null_default_value(value_type: Any) -> Any:
    """
    Default value used when a declaration is set to NULL.\n
    The keyword means "leave this slot empty" and every type has its own empty form, exactly the
    table documented by DatabasesSegmentValueChecker.null_parser. The value is produced directly
    here: the old code built a *text* like "" and pushed it back through the string parser, so a
    NULL string stole the next literal out of the string saving memory and every following
    statement silently got somebody else's value.

    :param value_type: Any    Declared python type of the column / segment.
    :return: Any
    """
    if isinstance(value_type, list):  # A whole table -> an empty table.
        return []
    match getattr(value_type, "__name__", str(value_type)):
        case "int":     return 0        # noqa
        case "float":   return 0.0      # noqa
        case "str":     return ""       # noqa
        case "bool":    return False    # noqa
        case "dict":    return {}       # noqa
        case "list":    return []       # noqa
        case _:         return None     # noqa
