from typing import Any

from src.innerpkg.mathmatics import comprehensive_calculator
from src.parseutil.kword import LEGAL_STRING_WORD
from src.innerpkg import packages
from src.parseutil.column import complex_data_type_checker


# ----- SOURCE START -----
#
# IDENTIFICATION SEGMENT PARSER. TO >>> EXECUTIVE SEGMENT PARSER.
#
# region
# INTRODUCE SENTENCE.
# ->
# ->
# ->
#
# CODE SEGMENT START.


class ReturnSegmentParser(object):
    def __init__(self, load_data: str) -> None:
        self._load_data = load_data.strip()[6:]

    def auto_check(self) -> Any:
        temp_string: str = ""

        # Start the loop to check the value in here.
        for load_char in self._load_data:
            if load_char in LEGAL_STRING_WORD:
                temp_string += load_char

    # IDENTIFICATION SEGMENT PART. TO >>> INNER PACKAGE CHECK SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def package_dispose(package_string: str) -> tuple[str, list[Any]]:
        """
        This function is used to
        :param package_string: str
        :return: tuple[str, list[Any]]
        """
        package_string:      str       = package_string.strip()
        temp_string_memory:  str       = ""
        final_return_string: str       = ""
        final_return_list:   list[Any] = []
        index:               int       = 0
        package_char:        str

        # Start to dispose the string in here.
        for index, package_char in enumerate(package_string):
            if package_char == '(':
                final_return_string = temp_string_memory.strip()
                temp_string_memory = ""  # Clean the memory.
                break  # Start the next loop.

            # Or anything else, we can just load the string into the temp memory.
            else:
                temp_string_memory += package_char

        # Initialize the value for next part of loop.
        deep_counter: int = 0

        # Start to dispose the argument in the function.
        for index, package_char in enumerate(package_string[index:]):
            if package_char == '(':
                deep_counter += 1
            elif package_char == ')':
                deep_counter -= 1
                if deep_counter == 0:
                    break

            # Check and add the argument into the list.
            if package_char == ',' and deep_counter == 1:
                final_return_list.append(complex_data_type_checker(temp_string_memory.strip())[0])
                temp_string_memory = ""  # Clean the memory.

            # Or anything else, just add it into the string.
            else:
                temp_string_memory += package_char

        # Finally, we can just return the value in here.
        return final_return_string, final_return_list

    @staticmethod
    def search_package(package_name: str, *args) -> Any:
        """

        :param package_name:
        :return:
        """
        master_info: str
        temp_string: str = ""

        # Start to search the package in here.
        for load_index, load_char in enumerate(package_name.strip()):
            if load_char == ".":  # If the character is a dot, then we need to check if the package exists.
                master_info = temp_string.strip()
                temp_string = package_name.strip()[load_index+1:]
                break

            # Or anything else, just append it into normal.
            else:
                temp_string += load_char

        # Or else, maybe this is not a correct package in here.
        else:
            raise TypeError("This may not a correct package in here.")

        # Start the next part: search the target package's address.
        match master_info:
            case "packages":   return packages.CHECKING_DICTIONARY[temp_string]()                           # noqa
            case "mathmatics": return comprehensive_calculator(True, (temp_string, *args))
            case _: raise KeyError(f"Unsupported data item: {package_name} + {args}")


# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
