import ctypes
from typing import Any

from src.v10.root.special_number import Infinite
from src.v10.struct.char import CALCULATE_CHAR
from src.v10.struct.signal import ValueFormatter


def calculate_dispose(first: Any, second: Any, event: str) -> Any:
    try:
        match event:
            case "+":  return first + second    # noqa
            case "-":  return first - second    # noqa
            case "*":  return first * second    # noqa
            case "/":  return first / second    # noqa
            case "**": return first ** second   # noqa
            case "//": return first // second   # noqa
            case "<<": return first << second   # noqa
            case ">>": return first >> second   # noqa
            case "&":  return first & second    # noqa
            case "|":  return first | second    # noqa
            case "^":  return first ^ second    # noqa
            case "<":  return first < second    # noqa
            case ">":  return first > second    # noqa
            case "<=": return first <= second   # noqa
            case ">=": return first >= second   # noqa
            case "==": return first == second   # noqa
            case "!=": return first != second   # noqa
            case "%":  return first % second    # noqa
            case _:    raise TypeError(event)   # noqa
    except ZeroDivisionError:
        return Infinite()


def calculate_dispose_string(saving_item: tuple[str | int, int],
                             left_string: tuple[str | int, int],
                             right_string: tuple[str | int, int]) -> tuple[str | int, int]:
    if saving_item[0] == "+":
        return (
            left_string[0] + right_string[0],  # noqa
            left_string[1] | right_string[1]
        )
    elif saving_item[0] == "*" and isinstance(left_string[0], str):
        return (
            left_string[0] * right_string[0],  # noqa
            left_string[1] | right_string[1]
        )
    elif saving_item[0] == "*" and isinstance(left_string[0], int):
        return (
            right_string[0] * left_string[0],  # noqa
            left_string[1] | right_string[1]
        )
    elif saving_item[0] == "%":
        return (
            left_string[0] % right_string[0],
            left_string[1] | right_string[1]
        )
    else:
        raise ValueError(f"Unknown operator: {saving_item[0]}")


def evaluate_stack(value: list[tuple[Any, ctypes.c_uint8]]) -> Any:
    """
    Reduce one value stack (a reverse-polish program stored inside a segment) into its value.

    A token is only treated as an operator when at least two operands are already waiting,
    otherwise a legitimate string value such as "-" would be mistaken for subtraction.

    :param value: list[tuple[Any, ctypes.c_uint8]]
    :return: Any
    """
    stack_load: list[Any] = []

    # Start the loop to parse the value.
    for item in value:
        if item[1] == ValueFormatter.OPERATION_SIGNAL_FORMATTER and item[0] in CALCULATE_CHAR and len(stack_load) >= 2:
            second_value: Any = stack_load.pop()
            first_value:  Any = stack_load.pop()
            stack_load.append(calculate_dispose(first_value, second_value, item[0]))
        else:
            stack_load.append(item[0])

    # When stack is empty, we can just return it as normal.
    if not stack_load:
        return None

    # We cannot clean the stack, so we can raise the exception.
    if len(stack_load) > 1:
        raise ValueError(
            "Incomplete expression while the value was reduced: "
            f"{len(stack_load)} operands were left without an operator."
        )

    # Finally, the item which just in stack is the target we need to return.
    return stack_load[0]
