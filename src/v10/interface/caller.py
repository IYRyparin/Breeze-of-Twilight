from typing import Any

from src.v10.struct import kword
from src.v10.interface import packages
from src.v10.interface.mathmatics import comprehensive_calculator


class CallSegmentParser(object):
    def __init__(self, load_data: str) -> None:
        self._load_data = load_data

    @staticmethod
    def package_dispose(package_string: str) -> tuple[tuple[str, list[Any]], int]:
        """
        This function is used to
        :param package_string: str
        :return: tuple[str, list[Any]]
        """
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
        if index < len(package_string) - 1:
            for index, package_char in enumerate(package_string[index:]):
                if package_char == '(':
                    deep_counter += 1
                elif package_char == ')':
                    deep_counter -= 1
                    if deep_counter == 0:  # Check the correct edge in here.
                        break

                # Check and add the argument into the list.
                if package_char == ',' and deep_counter == 1:
                    final_return_list.append(temp_string_memory.strip())
                    temp_string_memory = ""  # Clean the memory.

                # Or anything else, just add it into the string.
                else:
                    temp_string_memory += package_char

        # Some package which don't need argument can ignore bracket, we need to check in here.
        else:
            final_return_string = temp_string_memory

        # Finally, we can just return the value in here.
        return (final_return_string, final_return_list), index

    def search_package(self, package_name: str) -> tuple[Any, int]:
        """

        :param package_name:
        :return:
        """
        master_info: str
        temp_string: str = ""

        # Start to search the main package in here.
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

        # Start to search the sub package name, and get the argument's place.
        (sub_name, argument), index = self.package_dispose(temp_string)

        # Start the next part: search the target package's address.
        match master_info:
            case kword.ConfigurationInnerPackageKeyword.INNER_PACKAGES:
                return packages.CHECKING_DICTIONARY[sub_name](), index + 9
            case kword.ConfigurationInnerPackageKeyword.INNER_MATHEMATICS:
                return comprehensive_calculator(True, *(sub_name, *argument)), index + 12
            case _: raise NameError(f"Unsupported data item: {package_name} + {argument}")
