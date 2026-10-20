import re


def is_file_string_literal(value: str) -> bool:
    """Return whether the quoted value is a file path-like string."""
    if not value:
        return False
    file_pattern: str = r"^(?:\.{1,2}[\\/].*|(?:[a-zA-Z]:\\.{1,2})?[\\/](?:[^\\/?*|<>:\"]+[\\/])*(?:[^\\/?*|<>:\"]+?(?:\.[^.\\/?*|<>:\"]+)?)?)$"
    return bool(re.fullmatch(r"^\.{1,2}[\\/].*$", value)) or bool(re.fullmatch(file_pattern, value))
