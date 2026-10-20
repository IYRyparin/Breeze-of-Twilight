from src.v10.struct.signal import ValueFormatter


def get_priority_level(operate: str) -> int:
    priority_deque: dict[int, set[str]] = {
        5: {"(", ")", "[", "]", "{", "}"},
        4: {"**"},
        3: {"*", "/", "//"},
        2: {"+", "-"},
        1: {"<", ">", "<=", ">=", "==", "!=", "^", "&", "|", "<<", ">>", "%", "~"},
    }
    for key, value in priority_deque.items():
        if operate in value:
            return key
    return -1


def infix_to_postfix_with_list(infix: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """

    :param infix: Origin infix list.
    :return: list[tuple[str, int]]
    """
    final_return_list: list[tuple[str, int]] = []
    operation_stack: list[tuple[str, int]] = []
    operation_signal = ValueFormatter.OPERATION_SIGNAL_FORMATTER

    # Start the loop, check and change the list.
    for infix_item in infix:
        if infix_item[1] != operation_signal:
            final_return_list.append(infix_item)
            continue

        # Get the operator char, check the char type.
        operator = infix_item[0]

        # Check the bracket in here.
        if operator == "(":
            operation_stack.append(infix_item)
            continue
        elif operator == ")":
            while operation_stack and operation_stack[-1][0] != "(":
                final_return_list.append(operation_stack.pop())
            operation_stack.pop()
            continue

        # Pop with bracket in here.
        current_priority = get_priority_level(operator)
        while operation_stack and operation_stack[-1][0] != "(":
            stack_priority = get_priority_level(operation_stack[-1][0])
            if stack_priority < current_priority or (stack_priority == current_priority and operator == "**"):
                break
            final_return_list.append(operation_stack.pop())
        operation_stack.append(infix_item)

    # Pop with no bracket in here.
    while operation_stack:
        operator_item = operation_stack.pop()
        if operator_item[0] == "(":
            raise ValueError("Mismatched opening parenthesis in infix expression.")
        final_return_list.append(operator_item)

    # So finally, we can return the list in here.
    return final_return_list
