from src.v10.struct.char import CALCULATE_CHAR
from src.v10.struct.signal import ValueFormatter
from src.v10.valchk.infix.fixcalc import calculate_dispose
from src.v10.valchk.strchk.numcheck import int_literal_loader, decimal_literal_loader
from src.v10.root.decimal import ConversionDecimal
from src.v10.valchk.infix.fixcalc import calculate_dispose_string


def complex_mathematics_suffix_int_calculator(origin_data: list[tuple[str, int]],
                                              signal_check: bool = True) -> list[tuple[int | str, int]]:
    """
    This function is used to check and calculate the math string with int type.
    In here, we need to change the value into the correct type and return it with the correct format signal.
    Furthermore, we need to check the signal to make sure the value is correct.
    :param origin_data: list[tuple[int, int]]
    :param signal_check: bool
    :return: tuple[int, int]
    """
    calculate_stack: list[tuple[int | str, int]] = []

    # Range the postfix.
    for element_item in origin_data:
        if element_item[0] in CALCULATE_CHAR:
            right_value: tuple[int | str, int] = calculate_stack.pop()
            left_value:  tuple[int | str, int] = calculate_stack.pop()

            # Compare and return the correct method.
            if (right_value[1] >= ValueFormatter.SEPARATOR or left_value[1] >= ValueFormatter.SEPARATOR) and signal_check:
                calculate_stack.append(left_value)
                calculate_stack.append(right_value)
                calculate_stack.append(element_item)
            else:
                calculate_stack.append((calculate_dispose(left_value[0], right_value[0], element_item[0]), ValueFormatter.DEFAULT_EMPTY_FORMATTER))

        # Or anything else, we can just input it into the stack.
        else:
            calculate_stack.append((int_literal_loader(element_item[0])[0], element_item[1]))

    # So finally, we can just return it.
    return calculate_stack


def complex_mathematics_suffix_decimal_calculator(origin_data: list[tuple[str, int]], signal_check: bool = True) -> list[tuple[ConversionDecimal | str, int]]:
    """
    Welp...This function is used to check and calculate the math string.
    In here, we need to change the value into the correct type and return it with the correct format signal.
    :param origin_data: list[tuple[str, int]]
    :param signal_check: bool    Whether to check the value explain signal or not.
    :return: tuple[ConversionDecimal, int]
    """
    calculate_stack:      list[tuple[ConversionDecimal | str, int]] = []

    # Range the postfix.
    for element_item in origin_data:
        if element_item[0] in CALCULATE_CHAR:
            right_value: tuple[ConversionDecimal | str, int] = calculate_stack.pop()
            left_value:  tuple[ConversionDecimal | str, int] = calculate_stack.pop()

            # Compare and return the correct method.
            if (right_value[1] >= ValueFormatter.SEPARATOR or left_value[1] >= ValueFormatter.SEPARATOR) and signal_check:
                calculate_stack.append(left_value)
                calculate_stack.append(right_value)
                calculate_stack.append(element_item)
            else:
                calculate_stack.append((calculate_dispose(left_value[0], right_value[0], element_item[0]), left_value[1]))

        # Or anything else, we can just append it.
        else:
            calculate_stack.append((ConversionDecimal(decimal_literal_loader(element_item[0])[0]), element_item[1]))

    # Finally, anything is ok, so we can return it at all.
    return calculate_stack


def complex_string_suffix_calculator(string_load_list: list[tuple[str | int, int]]) -> list[tuple[str | int, int]]:
    """
    This function is used to check and merge the string with the correct format signal.
    How to merge the string? Well...it will follow those rules.\n
    - When the left and right side of the operator is not waiting for a format injection, it will merge the string.
    - When the left or right side of the operator is waiting for a format injection, it will not merge the string.
    :param string_load_list: list[str | int]
    :return: list[tuple[str | int, int]]
    """
    temp_load_stack:        list[tuple[str | int, int]] = []
    value_search_pointer:   int                         = 0

    # When nothing happens, we can just load it as normal.
    if len(string_load_list) > 0 and string_load_list[0][1] == ValueFormatter.DEFAULT_EMPTY_FORMATTER:
        return [string_load_list[0]]

    # Start the loop to merge the string in here.
    for saving_item in string_load_list:
        if saving_item[1] == ValueFormatter.OPERATION_SIGNAL_FORMATTER:  # Operators: merge only when neither side is waiting for a format injection.
            value_search_pointer += 1
            right_string: tuple[str | int, int] = temp_load_stack.pop()
            left_string:  tuple[str | int, int] = temp_load_stack.pop()

            # Check and merge the string with correct exec signal.
            if left_string[1] < ValueFormatter.SEPARATOR and right_string[1] < ValueFormatter.SEPARATOR:
                temp_load_stack.append(calculate_dispose_string(saving_item, left_string, right_string))

            # Or else, just return it as normal, follow LIFO, like nothing happen.
            else:
                temp_load_stack.append(left_string)
                temp_load_stack.append(right_string)
                temp_load_stack.append(saving_item)

            continue

    # Finally, return the stack here.
    return temp_load_stack
