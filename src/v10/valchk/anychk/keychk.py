from typing import Any

from src.v10.root.special_number import NotANumber, Infinite
from src.v10.struct import kword


def special_keyword_changer(value: str) -> Any:
    match value:
        case kword.ConfigurationValueReplacerKeyword.TRUE: return True
        case kword.ConfigurationValueReplacerKeyword.FALSE: return False
        case kword.ConfigurationValueReplacerKeyword.NULL: return None
        case kword.ConfigurationValueReplacerKeyword.INF: return Infinite()
        case kword.ConfigurationValueReplacerKeyword.NAN: return NotANumber()
        case _: raise ValueError(f"Unsupported special keyword: {value}")
