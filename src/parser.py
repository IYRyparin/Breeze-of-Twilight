from src.parseutil.kword import ConfigurationStatusExecutiveKeyword
from src.parsefunc import function
from src.parseutil import kword as keyword
from src.parseutil.structure import ConfigurationSignalStructure, ConfigurationDataStandaloneSegmentStructure
from src.parsecheck.check import start_check, ReplacerDatabase
from src.parseutil.column import *


# ----- SOURCE START -----
#
# ----- SEPARATING LINE -----
#
# IDENTIFICATION GLOBAL CLASS. TO >>> CONFIGURATION PARSER.
#
# region
# INTRODUCE SENTENCE.
# -> Those class defines the main part of BOT's parser. From here, it can realize the parser's executive and data's call.
# -> After that, we need to start to build the configuration parser, which is the main part of BOT's file, it can save the critical information which will be used to execute the BOT file.
# -> So from that, I need to build a configuration parser to realize it.
# -> Furthermore, Because it is not similar to JSON, we need to build more complex method such as conversion part.
# -> So we cannot just use a dict to save the data, we need to build a custom class to save the data, and we can use this class to parse the data and build grammar tree.
# -> So from that, I need to build a custom class to realize it.
#
# region
# CONFIGURATION PARSER CODE SEGMENT START.


class ConfigurationStandalone(object):
    # Configuration's basic information.
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+
    # |        NAME          |                        TYPE                           |          VALUE                |             EXPLAIN               |
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+
    CONFIGURATION_ID:         str                                                    = "N/A"
    CONFIGURATION_VERSION:    float                                              = 0.0
    CONFIGURATION_ENCODE:     str                                                    = "utf-8"
    CONFIGURATION_READONLY:   bool                                                   = False
    _basic_signal:            ConfigurationSignalStructure                           = ConfigurationSignalStructure()
    _dictionary:              dict[str, ConfigurationDataStandaloneSegmentStructure] = {}                              # This is the final grammar tree, which will be built and returned.
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+

    def __init__(self, string: str) -> None:
        """
        This is a BOT Configuration class. Maybe you're questioning why I don't use dict type, right?
        As you know, it has some special part like conversion value that dict may not support.
        So from that, I define a custom class to realize it.
        :param: string: str   Origin Code string.
        """
        start_check(string=string)

        # Load some basic information from the string, and then we can start to parse the data's part.
        self._string_memory, self._basic_string = self._data_load_string(string=string)  # Save the string, make sure that it will not be broken in string-breaking part.

        # Replace the '\n' into empty string, ready to start of the next part.
        self._basic_string = self._basic_string.lower()

        # Initialize some value, and start to parse the data's part.
        self._local_index:         int       = 0
        self._origin_grammar_list: list[str] = []

        # Clear the grammar list (still useful for title parsing).
        for segment in list(filter(lambda n: n != "", self._basic_string.strip().split(";"))):
            self._origin_grammar_list.append(segment.strip())

        # Parse title lines until databases-start keyword is encountered.
        for grammar_parse_index, grammar_parse_element in enumerate(self._origin_grammar_list):
            words:         list[str] = grammar_parse_element.split()

            # Check the start signal, if it is, jump out the title parse to save time.
            if keyword.ConfigurationKeyword.KEYWORD_DATABASES_START in words or keyword.ConfigurationKeyword.KEYWORD_CONVERSION_START in words:
                break

            # Load title, increase the index and prepare for next loop.
            self._data_load_title(grammar_parse_element)
            self._local_index += 1

        # Or anything else, raise the Exception.
        else:
            raise SyntaxError("Cannot found the DATABASE division.")

        # Robustly extract the databases block from the raw basic string using brace matching.
        def _find_matching_brace(s: str, start_index: int) -> int:
            """

            :param s:
            :param start_index:
            :return:
            """
            string_mode: bool = False
            i = start_index
            depth = 0
            while i < len(s):
                ch = s[i]
                if ch == '"' and (i == 0 or s[i-1] != '\\'):
                    string_mode = not string_mode
                if not string_mode:
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            return i
                i += 1
            raise SyntaxError('Unmatched brace in databases block')

        def _split_top_level_statements(s: str) -> list:
            parts = []
            buf = ''
            string_mode = False
            depth = 0
            i = 0
            while i < len(s):
                ch = s[i]
                if ch == '"' and (i == 0 or s[i-1] != '\\'):
                    string_mode = not string_mode
                    buf += ch
                    i += 1
                    continue
                if not string_mode:
                    if ch in '{[(':
                        depth += 1
                    elif ch in '}])':
                        depth -= 1
                    if ch == ';' and depth == 0:
                        parts.append(buf.strip())
                        buf = ''
                        i += 1
                        continue
                buf += ch
                i += 1
            if buf.strip() != '':
                parts.append(buf.strip())
            return parts

        # find the 'databases-start' keyword in the basic string
        ds_idx:        int = self._basic_string.find(keyword.ConfigurationKeyword.KEYWORD_DATABASES_START)
        brace_idx:     int = self._basic_string.find('{', ds_idx)
        match_idx:     int = _find_matching_brace(self._basic_string, brace_idx)
        block_content: str = self._basic_string[brace_idx + 1 : match_idx]       # noqa

        # split into top-level statements
        db_statements: list[str] = _split_top_level_statements(block_content)

        # parse the database statements into dictionary
        self._data_load_databases(db_statements, self._dictionary)

        # Conversion part parsing not implemented in this simplified parser iteration.
        # TODO: implement conversion-start/conversion-end handling if needed.

    # IDENTIFICATION SEGMENT PART. TO >>> INITIALIZE SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, we need to initialize the configuration's basic information, and then we can start to parse the data's part.
    # -> In here,
    # ->
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def _data_load_string(string: str) -> tuple[Queue[str], str]:
        """
        In here, this function is used to check and load the
        :return: list[str]
        """
        # +----------+------+-------+--------------------+
        # |   NAME   | TYPE | VALUE |      EXPLAIN       |
        # +----------+------+-------+--------------------+
        string_signal: bool = False  # Signal in string or not.
        input_signal:  bool = True  # Signal in announcement or not.
        basic_string:  str  = ""     # String which is changed.
        # +----------+------+-------+--------------------+

        # ----- CONDITION SEGMENT -----
        #
        # region
        # INTRODUCE SENTENCE.
        # -> Start the loop and find the announcement line.
        #
        # CODE SEGMENT PART START.

        for index, char in enumerate(string):
            if (char == "\"" and index >= 1 and string[index - 1] != "\\") or (char == "\"" and index == 0):
                string_signal = not string_signal

            # noqa A special signal, used to replace the semicolon in string, because the semicolon is used to split the grammar, so we need to replace it into another safe value.
            elif char == ";" and string_signal:
                # Replace semicolon inside string with placeholder to avoid splitting grammar by it
                basic_string += "\uFFFE"    # noqa
                continue

            # When we find the announcement signal, we need to change the signal to True, and then we can start to drop the announcement part.
            elif char == "\n" and not input_signal:
                input_signal = True

            # When we in the string part, so it means that we don't need to care about the data, just drop it off.
            if not input_signal:
                continue

            # Or anything else, we need to check out the announcement signal, and then we can start to parse it.
            else:
                if char == "#" and not string_signal:
                    input_signal = False

                # On other part, we can just add the signal into the string.
                else:
                    basic_string += char

        # CODE SEGMENT PART END.
        # endregion
        #
        # ----- SEGMENT END -----

        # Replace change line's element to empty string, make sure it won't break the parse.
        basic_string: str = basic_string.replace("\n", "")
        del string_signal, input_signal, char, index

        # Export the basic value which maybe used when parsing the data, even though their value just is NoneType.
        # +----------------------------+----------------------+-----------------------+----------------------+
        # |            NAME            |         TYPE         |          VALUE        |       EXPLAIN        |
        # +----------------------------+----------------------+-----------------------+----------------------+
        _is_string_signal:              bool                  = False                  # A boolean signal which used to explain this part is in string or not.
        _temp_memory_string:            str                   = ""                     # A temp value, used to save the string.
        _temp_memory_string_saver:      Queue[str]            = Queue()                # We need to save the string, or it will be breaked.
        # +----------------------------+----------------------+-----------------------+----------------------+

        # ----- CONDITION SEGMENT -----
        #
        # region
        # INTRODUCE SENTENCE.
        # -> Start the basic check, push out the string value and save it into temp list.
        #
        # CODE SEGMENT PART START.

        for index, one_char in enumerate(basic_string):
            if one_char == "\"":  # To index the setter, we need to make sure it is not out of range.
                _is_string_signal = not _is_string_signal

                # When this value change True to False, means it is go out to string right now.
                if not _is_string_signal:  # Before to save it, we must replace the special part in here.
                    for key, value in ReplacerDatabase.SPECIAL_CHARACTER_REPLACER_DICT.items():
                        _temp_memory_string = _temp_memory_string.replace(key, value)

                    # After the replacement, we can save it and clear the buffer now.
                    _temp_memory_string_saver.put(_temp_memory_string)  # Append the string into queue to save it.
                    _temp_memory_string = ""  # Flush the temp string for prepare to the next string value.

            # If it is in the string, we need to start to push the string into the saving value.
            elif _is_string_signal and one_char is not None:
                _temp_memory_string += one_char

        # CODE SEGMENT PART END.
        # endregion
        #
        # ----- SEGMENT END -----

        # At finally, we can return the information.
        return _temp_memory_string_saver, basic_string

    def _data_load_title(self, title_element: str) -> None:
        """
        This function is used to load the title.
        Only used in the standalone mode, because the title is not needed in the database mode.
        :param title_element: str   The title element which will be loaded.
        :return: None
        """
        title_element: str = title_element.strip()

        # Drop off the useless part.
        if title_element == "":
            return

        # Start to check the segment, input the useful part into the structure.
        try:
            title_configuration_describe, title_configuration_value = list(filter(lambda n: n != "", title_element.split(" ")[1: 3]))

        # When sometimes we get the empty value, so we need to drop out it.
        except ValueError:
            return

        # Match and check the value.
        match title_configuration_describe:
            case keyword.ConfigurationKeyword.KEYWORD_CONFIGURE_ID:  # Load configuration id, get the id's string from string's memory.
                self.CONFIGURATION_ID = self._string_memory.get()

            # Load configuration version into the value.
            case keyword.ConfigurationKeyword.KEYWORD_CONFIGURE_VERSION:
                self.CONFIGURATION_VERSION = float(ConversionDecimal(title_configuration_value).auto_changer())

            # Load configuration's readonly info into the value.
            case keyword.ConfigurationKeyword.KEYWORD_CONFIGURE_READONLY:
                self.CONFIGURATION_READONLY = DatabasesSegmentValueChecker.boolean_parser(title_configuration_value, None)

            # Load configurations encode info into the value.
            case keyword.ConfigurationKeyword.KEYWORD_CONFIGURE_ENCODE:
                self.CONFIGURATION_ENCODE = self._string_memory.get()

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> PARSE UTIL SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, we can start to parse the data's part and merge it into the structure.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def _find_matching_brace_static(s: str, start_idx: int) -> int:
        string_mode: bool = False
        i: int = start_idx
        depth: int = 0
        while i < len(s):
            ch: str = s[i]
            if ch == '"' and (i == 0 or s[i-1] != '\\'):
                string_mode = not string_mode
            if not string_mode:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return i
            i += 1
        raise SyntaxError('Unmatched brace')

    @staticmethod
    def _split_top_level_statements_static(s: str) -> list:
        parts:       list[str] = []
        buf:         str = ''
        string_mode: bool = False
        depth:       int = 0
        i:           int = 0

        # Start the loop to check the ';' to split sentence in here.
        while i < len(s):
            ch = s[i]
            if ch == '"' and (i == 0 or s[i-1] != '\\'):
                string_mode = not string_mode
                buf += ch
                i += 1
                continue
            if not string_mode:
                if ch in '{[(':
                    depth += 1
                elif ch in '}])':
                    depth -= 1
                if ch == ';' and depth == 0:
                    parts.append(buf.strip())
                    buf = ''
                    i += 1
                    continue
            buf += ch
            i += 1
        if buf.strip() != '':
            parts.append(buf.strip())
        return parts

    def _data_load_databases(self, load_data: list[str], base_dictionary: dict) -> None:
        """
        This function is used to load the databases part.
        Only used in the standalone mode, because the databases is not needed in the database mode.
        :param load_data: list[str]
        :return: None
        """
        element_data_index: int                         = 0
        element_data_item:  str

        # Start the loop and check the data.
        while element_data_index < len(load_data):
            element_data_item = load_data[element_data_index]

            # Drop out the empty part to save time and keep stable.
            if element_data_item == "":
                element_data_index += 1
                continue

            # +----------------+--------------------------------------------+-------------------------------------------------+--------------------------------------+
            # |      NAME      |                   TYPE                     |                      VALUE                      |                 EXPLAIN              |
            # +----------------+--------------------------------------------+-------------------------------------------------+--------------------------------------+
            segment_structure:  ConfigurationDataStandaloneSegmentStructure = ConfigurationDataStandaloneSegmentStructure()    # A structure which used to save the final data.
            temp_string_memory: str                                         = ""                                               # Save the string temporary.
            store_start_index:  int                                         = 0                                                # Save the start index of the section in the sentence.
            store_end_index:    int                                                                                            # Save the end index of the section in the sentence.
            # +----------------+--------------------------------------------+-------------------------------------------------+--------------------------------------+

            # Load some initialize value and prepare for the loop.
            element: str = element_data_item.lstrip()
            leading_offset: int = len(element_data_item) - len(element)

            # Start next loop and check the value. We can check the name part.
            for column_index, column_char in enumerate(element):
                if column_char in LEGAL_STRING_WORD:
                    temp_string_memory += column_char

                # After that, we can start to search the end signal of the data.
                elif column_char == "[":
                    store_start_index = column_index + leading_offset
                    break

                # Other characters (spaces, punctuation) — ignore and continue scanning.
                else:
                    continue

            # If we didn't find a start bracket, skip this element.
            if store_start_index == 0:
                element_data_index += 1
                continue

            # Merge the data into the structure, and increase the number.
            segment_structure.name = element_data_item[ : store_start_index].strip()  # noqa
            store_start_index += 1

            # Start to search the type's limit in here.
            store_end_index = element_data_item.find("=", store_start_index)
            type_checker: DatabasesSegmentTypeChecker = DatabasesSegmentTypeChecker()

            # Start to search the end signal of the type, means ']'.
            while element_data_item[store_end_index] != ']':
                store_end_index -= 1

                # Check the index, make sure it is in the correct part.
                if store_end_index < 0:
                    raise ValueError("Invalid format: Missing closing bracket ']'")

            # Start to check the value in here.
            temp_load: str = element_data_item[store_start_index : store_end_index]  # noqa
            sub_index: int = temp_load.find("<")  # noqa

            # if sub index is -1, means that we don't need to care about the angle bracket.
            if sub_index == -1:
                segment_structure._probable_type = type_checker.dict_checker(temp_load)(temp_load, self._string_memory)  # noqa

            # Or anything else, we need to change a little.
            else:
                segment_structure._probable_type = type_checker.dict_checker(temp_load[ : sub_index])(temp_load, self._string_memory)  # noqa

            # Add the edge signal, prepare for keyword checker.
            store_end_index += 1
            store_start_index = store_end_index

            # Start to search the '=' edge.
            while element_data_item[store_end_index] != '=':
                store_end_index += 1

            # Get the edge, load and check this value is constant or mutable.
            modify_string_part: str = element_data_item[store_start_index : store_end_index].strip()  # noqa

            # In here, start to check the constant status.
            if modify_string_part == keyword.ConfigurationDataExecutiveKeyword.EXECUTIVE_KEYWORD_CONST:
                segment_structure._changeable = False

            # Check the mutable status.
            elif modify_string_part == keyword.ConfigurationDataExecutiveKeyword.EXECUTIVE_KEYWORD_MUTABLE:
                segment_structure._changeable = True

            # Change the index, prepare for the value.
            store_end_index += 1
            store_start_index = store_end_index
            value_checker: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker(*segment_structure.probable_type)

            # Start to initialize some basic value to prepare for the parse.
            string_signal:     bool = False
            extension_require: bool = True

            # Start to search the end of the value's edge.
            try:
                while not (element_data_item[store_end_index + 1] == '>' and element_data_item[store_end_index] == '-' and not string_signal):
                    if element_data_item[store_end_index + 1] == "\"" and element_data_item[store_end_index] != "\\":
                        string_signal = not string_signal

                    # Nothing need to care about, we can just continue.
                    store_end_index += 1

            # Get the exception, means that there don't have any extension require part, so we can just use full line.
            except IndexError:
                extension_require = False

            # At finally, start to input the value into the structure.
            finally:  # When no extension require, it points to the end of the string. But then it has, it points to the place where '-' signal occurred, so we need to care about this.
                value_string_part: str = element_data_item[store_start_index : store_end_index + int(not extension_require)]  # noqa
                segment_structure._value_origin = value_string_part
                rhs_value: str = value_string_part.strip()

                # Search the null keyword, and replace it into the other part of value.
                temp_list: list[str] = rhs_value.split(" ")

                # Start the loop. Search the special keyword and replace it.
                for temp_index, temp_item in enumerate(temp_list):
                    if temp_item == ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_NULL:
                        if segment_structure.probable_type[-1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
                            temp_list[temp_index] = "[]"
                        else:
                            temp_list[temp_index] = str(value_checker.null_parser("", segment_structure.probable_type[0]))

                # Save the list into the string (preserve spaces).
                value_string_part = ' '.join(temp_list)

                # IDENTIFICATION SEGMENT PART. TO >>> DICT PARSING SEGMENT.
                #
                # region
                # INTRODUDCE SENTENCE.
                # -> Because we need to check the special data info, so we need to check the type at first.
                #
                # CODE SEGMENT PART START.

                if segment_structure.probable_type == ([dict], TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN):
                    inner_brace_idx = value_string_part.find('{')

                    # If the value contains an inline '{...}' block, extract inner statements and recurse.
                    if inner_brace_idx != -1:
                        try:
                            inner_end = self._find_matching_brace_static(value_string_part, inner_brace_idx)

                        # fallback: treat as empty dict.
                        except SyntaxError:
                            segment_structure._value = {}

                        # Load value into the normal mode.
                        else:
                            inner_content = value_string_part[inner_brace_idx + 1: inner_end]
                            child_statements = self._split_top_level_statements_static(inner_content)
                            segment_structure._value = {}
                            self._data_load_databases(child_statements, segment_structure.value)

                    # no inline block — treat as empty dict.
                    else:
                        segment_structure._value = {}

                    # store parent dict node and move to next top-level element.
                    base_dictionary[segment_structure.name] = segment_structure
                    element_data_index += 1
                    continue

                # CODE SEGMENT PART END.
                # endregion
                #
                # ----- SEPARATING LINE -----
                #
                # IDENTIFICATION SEGMENT PART. TO >>> LIST PARSER SEGMENT.
                #
                # region
                # INTRODUCE SENTENCE.
                # ->
                #
                # CODE SEGMENT PART START.

                elif segment_structure.probable_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
                    store_start_index, store_end_index = brackets_edge_index_checker(
                        dat_info_string=value_string_part,
                        right_move=0,
                        left_bracket='[',
                        right_bracket=']',
                        string_ignore=True
                    )

                    # Start to list the element.
                    segment_structure._value = self._data_load_table(
                        value_string_part[store_start_index + 1 : store_end_index],  # noqa
                        segment_structure.probable_type[0],
                        segment_structure.changeable
                    )

                # CODE SEGMENT PART END.
                # endregion
                #
                # ----- SEPARATING LINE -----
                #
                # IDENTIFICATION SEGMENT PART. TO >>> NORMAL VALUE CHECK SEGMENT.
                #
                # region
                # INTRODUCE SENTENCE.
                # ->
                #
                # CODE SEGMENT PART START.

                elif segment_structure.probable_type[1] == TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN:
                    parser_func = value_checker.auto_check(segment_structure.probable_type[0][0].__name__)

                    # single simple type, parse RHS.
                    if parser_func is None:
                        ldr_value: Any = complex_data_type_checker(value_string_part)[0]
                        segment_structure._value = self._string_memory.get() if isinstance(ldr_value, str) else ldr_value

                    # Or else, just load it with normal mode.
                    else:
                        segment_structure._value = parser_func(value_string_part, self._string_memory)

                # CODE SEGMENT PART END.
                # endregion

            # Start to check the extension require part.
            if extension_require:
                self._data_load_extension(
                    segment_structure_item=segment_structure,
                    load_data=element_data_item[store_end_index + 2 : ],  # noqa
                    data_type=segment_structure.probable_type[0][0] if len(segment_structure.probable_type[0]) == 1 else Any
                )

            # After that, all is ok, so we can just input it into the dictionary.
            base_dictionary[segment_structure.name] = segment_structure
            element_data_index += 1
            continue

    def _data_load_table(self, load_data_string: str, table_type: list[type], father_mutable: bool) -> list[ConfigurationDataStandaloneSegmentStructure]:
        """

        :param load_data_string: str
        :return: list[str]
        """
        final_saving_list: list[ConfigurationDataStandaloneSegmentStructure] = []
        type_counter:      function.Counter                                  = function.Counter(0)
        index_counter:     function.Counter                                  = function.Counter(0)
        string_signal:     bool                                              = False
        temp_data:         str                                               = ""
        block_counter:     int                                               = 0

        # Start the loop to check the data.
        for table_data_index, table_data_char in enumerate(load_data_string):
            segment_structure: ConfigurationDataStandaloneSegmentStructure = ConfigurationDataStandaloneSegmentStructure()

            # Check the string signal.
            if (table_data_index == 0 and table_data_char == "\"") or (table_data_index >= 1 and table_data_char == "\"" and load_data_string[table_data_index - 1] != "\\"):
                string_signal = not string_signal

                # Check the string signal, get the string and put it into the temp memory.
                if not string_signal:
                    temp_data = self._string_memory.get()  # Because this string may have been broken, so load from memory to change it.
                    continue

            # Start to check the data's terminate signal.
            elif (table_data_char == "," and not string_signal and block_counter == 0) or table_data_index == len(load_data_string) - 1 and temp_data.strip() != "":
                type_loader: type | list[type] = table_type[type_counter]  # Load the counter.
                temp_data = temp_data.strip()

                # Initialize the structure.
                segment_structure.name          = str(int(index_counter))
                segment_structure.changeable    = father_mutable
                segment_structure._value_origin = temp_data

                # Start to check the value.
                if isinstance(type_loader, list):
                    if temp_data.startswith("["): temp_data = temp_data[1 : ]   # noqa
                    if temp_data.endswith("]"):   temp_data = temp_data[ : -1]  # noqa
                    segment_structure._value = self._data_load_table(temp_data, type_loader, father_mutable)  # Start next loop.
                    continue

                # Or this value is a dict, so that we need to use dict loader.
                elif type_loader == dict:
                    if temp_data.startswith("{"): temp_data = temp_data[1 : ]   # noqa
                    if temp_data.endswith("}"):   temp_data = temp_data[ : -1]  # noqa
                    segment_structure._value = {}
                    self._data_load_databases(temp_data.split(";"), segment_structure.value)
                    continue

                # Anything else, we can just start the normal checking.
                value_checker: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker(None, None)

                # Start the check.
                value_load: Any = value_checker.auto_check(type_loader.__name__)  # noqa

                # If return None, we can start to complex check.
                if value_load is None:
                    segment_structure._value = complex_data_type_checker(temp_data)[0]  # noqa

                # Or anything else, just load in normal mode.
                else:
                    segment_structure._value = value_load(temp_data)

                # Save parsed element into the result list
                final_saving_list.append(segment_structure)

            # When we meet the block, we need to change the counter.
            elif table_data_char == "[": block_counter += 1  # noqa
            elif table_data_char == "]": block_counter -= 1  # noqa

            # Or anything else, we can just add it into the string.
            temp_data += table_data_char

        # Finally, we can return it.
        return final_saving_list

    def _data_load_extension(self,
                             segment_structure_item: ConfigurationDataStandaloneSegmentStructure,
                             load_data: str,
                             data_type: type) -> None:
        """

        :param load_data: str
        :param data_type: type
        :param segment_structure_item: ConfigurationDataStandaloneSegmentStructure
        :return: None
        """
        extension_index:   int                                    = 0
        temp_string:       str                                    = ""
        explain_info:      list[tuple[Any, c_uint8]]              = []
        extension_char:    str

        # Start the range to check the extension regular.
        while extension_index < len(load_data):
            extension_char = load_data[extension_index]  # Push the char into the temp memory.

            # Check the terminate signal.
            if extension_char == "(":
                extend_end_index: int = first_signal_edge_checker(load_data[extension_index : ], "(", ")") + extension_index  # noqa

                # Start to check the first edge in here.
                match temp_string.strip():
                    case ConfigurationExtensionKeyword.EXECUTIVE_KEYWORD_LIMIT:  # Limit rule.
                        explain_info: list[tuple[Any, ctypes.c_uint8]] = DatabaseSegmentExtensionRequireChecker().limit_rule_explain(
                            dat_info_string=load_data[extension_index + 1 : extend_end_index],  # noqa
                            value_type=data_type,
                            string_saving_memory=self._string_memory
                        )

                    # String regular checker.
                    case ConfigurationExtensionKeyword.EXECUTIVE_KEYWORD_REGULAR:
                        explain_info: list[tuple[Any, ctypes.c_uint8]] = DatabaseSegmentExtensionRequireChecker().regular_rule_explain(
                            dat_info_string=load_data[extension_index + 1 : extend_end_index],  # noqa
                            string_saving_memory=self._string_memory
                        )

                    # Or anything don't supported, raise the Exception.
                    case _:
                        raise IndexError("Unsupported explain code: " + temp_string.strip())

                # Load the rule into the structure.
                segment_structure_item.limit_value_list.extend(explain_info)

                # Finally, jump out to the next index.
                extension_index = extend_end_index + 1

            # Or anything else, just increase the index.
            else:
                temp_string += extension_char
                extension_index += 1

    def _data_load_conversion(self, load_data: list[str]) -> None:
        """

        :param load_data: list[str]
        :return: None
        """
        pass  # TODO: Fix the conversion parsing part.

    @property
    def dictionary(self):
        return self._dictionary


# CONFIGURATION PARSER CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
