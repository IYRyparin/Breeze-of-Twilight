from src.parsecheck.check import start_check
from src.parseutil.column import *
from src.parseutil.structure import ConfigurationDataStandaloneSegmentStructure


# ----- SOURCE START -----
#
# IDENTIFICATION ASSIST FUNCTION. TO >>> SPECIAL KEYWORD VALUE PARSE ASSIST.
#
# region
# INTRODUCE SENTENCE.
# -> The escape toolkit (is_escaped_char / unescape_string / ESCAPE_SEQUENCE_DICT) lives in
# -> src/parseutil/column.py, because the literal extractor, every bracket matcher and the value
# -> parsers all have to agree on what an escaped quote is. It is re-exported here by the
# -> `from src.parseutil.column import *` above.
#
# CODE SEGMENT START.


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


# CODE SEGMENT END.
# endregion
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
# CODE SEGMENT START.


class ConfigurationStandalone(object):
    # Configuration's basic information.
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+
    # |        NAME          |                        TYPE                           |          VALUE                |             EXPLAIN               |
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+
    CONFIGURATION_ID:         str                                                    = "N/A"
    CONFIGURATION_VERSION:    float                                              = 0.0
    CONFIGURATION_ENCODE:     str                                                    = "utf-8"
    CONFIGURATION_READONLY:   bool                                                   = False
    # This is the final grammar tree, which will be built and returned.
    # NOTE: it is declared here only for typing - the real (and per instance!) tree is created
    # inside __init__, see the comment there.
    _dictionary:              dict[str, ConfigurationDataStandaloneSegmentStructure] = {}
    # +----------------------+-------------------------------------------------------+-------------------------------+-----------------------------------+

    def __init__(self, string: str) -> None:
        """
        This is a BOT Configuration class. Maybe you're questioning why I don't use dict type, right?
        As you know, it has some special part like conversion value that dict may not support.
        So from that, I define a custom class to realize it.
        :param: string: str   Origin Code string.
        """
        start_check(string=string)  # Check there are any syntax error or not.

        # Load some basic information from the string, and then we can start to parse the data's part.
        self._string_memory, self._basic_string = self._data_load_string(string=string)  # Save the string, make sure that it will not be broken in string-breaking part.
        self._basic_string = self._basic_string.lower()

        # CRITICAL: the grammar tree MUST be per instance.
        # It used to live on the class, so every configuration ever parsed shared one dictionary:
        # loading file B silently injected all of B's keys into every earlier file too.
        self._dictionary: dict[str, ConfigurationDataStandaloneSegmentStructure] = {}
        self._local_index:         int       = 0
        self._origin_grammar_list: list[str] = []

        # Clear the grammar list (still useful for title parsing).
        for segment in list(filter(lambda n: n != "", self._basic_string.strip().split(";"))):
            self._origin_grammar_list.append(segment.strip())

        # Parse title lines until databases-start keyword is encountered.
        for grammar_parse_index, grammar_parse_element in enumerate(self._origin_grammar_list):
            words: list[str] = grammar_parse_element.split()
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
                if ch == '"' and not is_escaped_char(s, i):
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
                if ch == '"' and not is_escaped_char(s, i):
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

        # Grammar.bnf closes the section with 'DATABASES-END;'. Without that check a truncated
        # file is silently accepted as a complete one, so the trailing keyword is required here.
        if self._basic_string.find(keyword.ConfigurationKeyword.KEYWORD_DATABASES_END, match_idx) == -1:
            raise SyntaxError("Cannot found the DATABASES-END division, the file may be truncated.")

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
            # Escape aware toggling: the naive "previous char is a backslash" test broke on a
            # literal ending in "\\", which then swallowed the rest of the file into the string.
            if char == "\"" and not is_escaped_char(string, index):
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
        # Here the strings are pulled out of the code and pushed into the saving memory.
        # Escape aware toggling matters on BOTH places: the inductor above and this extractor
        # below. They used to disagree (only one of them checked the leading backslash), so a
        # literal \" silently ended or restarted a string in one of the two passes and every
        # later statement read somebody else's string.
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
            _is_escaped: bool = is_escaped_char(basic_string, index)

            if one_char == "\"" and not _is_escaped:  # To index the setter, we need to make sure it is not out of range.
                _is_string_signal = not _is_string_signal

                # When this value change True to False, means it is go out to string right now.
                if not _is_string_signal:  # Before to save it, we must replace the special part in here.
                    _temp_memory_string_saver.put(unescape_string(_temp_memory_string))  # Append the string into queue to save it.
                    _temp_memory_string = ""  # Flush the temp string for prepare to the next string value.

            # If it is in the string, we need to start to push the string into the saving value.
            elif _is_string_signal and one_char is not None:
                _temp_memory_string += one_char

        # An unterminated quote means the file itself is broken: report it now instead of
        # letting every later statement silently steal someone else's string.
        if _is_string_signal:
            raise SyntaxError("Unterminated string literal, please check the \" signals in the file.")

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
        element_data_index: int = 0
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
                type_word: str = temp_load.strip().lower()
                segment_structure._probable_type = type_checker.dict_checker(temp_load)(temp_load, self._string_memory)  # noqa

            # Or anything else, we need to change a little.
            else:
                type_word = temp_load[ : sub_index].strip().lower()  # noqa
                segment_structure._probable_type = type_checker.dict_checker(temp_load[ : sub_index])(temp_load, self._string_memory)  # noqa

            # ENUM<...> does not change the storage type (ANYTHING) but restricts the legal
            # values, exactly like "-> LIMIT(...)", so the candidates become a limitation rule.
            if type_word == keyword.ConfigurationValueType.VALUE_ENUM:
                for enum_value in type_checker.enum_values(temp_load, self._string_memory):
                    segment_structure.limit_value_list.append(
                        (enum_value, ExtensionExplainFormatter.LIMIT_WITHIN_VALUE)
                    )

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
            extension_require: bool = False
            value_end_index:    int  = len(element_data_item)      # Exclusive end of the value part.

            # Start to search the end of the value's edge: the '->' that introduces a limitation.
            # The scan walks the value itself with escape aware quote tracking; the old version
            # looked at "[index + 1]" to find its quotes, so a value written right after '=' such
            # as `NAME [STR] CST="a -> b";` never saw its own opening quote and everything after
            # the arrow inside the string was treated as a limitation rule.
            string_signal: bool = False
            scan_index:    int  = store_end_index

            while scan_index < len(element_data_item):
                scan_char: str = element_data_item[scan_index]

                if scan_char == "\"" and not is_escaped_char(element_data_item, scan_index):
                    string_signal = not string_signal

                elif not string_signal and scan_char == "-" and (
                        scan_index + 1 < len(element_data_item) and element_data_item[scan_index + 1] == ">"
                ):
                    extension_require = True
                    value_end_index = scan_index                   # The value stops right before '->'.
                    break

                scan_index += 1

            # 'store_end_index' keeps pointing at the place the extension part starts from, which
            # is the '-' of '->' when a limitation was found, or one past the value otherwise.
            store_end_index = value_end_index

            # Start to input the value into the structure.
            value_string_part: str = element_data_item[store_start_index : value_end_index]
            segment_structure._value_origin = value_string_part
            rhs_value: str = value_string_part.strip()

            # NULL empties the whole slot. Handling it here (instead of rewriting the value text
            # and pushing it back through the value parsers) keeps the storage coherent: nothing
            # gets taken from the string saving memory for a value that never had a literal.
            if rhs_value.lower() == keyword.ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_NULL:
                self._apply_null_value(segment_structure)

            else:
                self._apply_value_expression(segment_structure, value_string_part, value_checker)

            # Start to check the extension require part.
            if extension_require:
                self._data_load_extension(
                    segment_structure_item=segment_structure,
                    load_data=element_data_item[store_end_index + 2 : ],  # noqa - skip the '->' signal.
                    data_type=segment_structure.probable_type[0][0] if len(segment_structure.probable_type[0]) == 1 else Any
                )

            # After that, all is ok, so we can just input it into the dictionary.
            base_dictionary[segment_structure.name] = segment_structure
            element_data_index += 1
            continue

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> NULL VALUE SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> NULL empties the slot. Doing it here instead of rewriting the value text keeps the
    # -> string saving memory untouched, so neighbours never lose their literal.
    #
    # CODE SEGMENT PART START.

    @staticmethod
    def _apply_null_value(segment_structure: ConfigurationDataStandaloneSegmentStructure) -> None:
        """
        Fill one segment with the empty value of its declared type.

        :param segment_structure: ConfigurationDataStandaloneSegmentStructure
        :return: None
        """
        column_types: list = segment_structure.probable_type[0]

        # A table stays an empty list of rows.
        if segment_structure.probable_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
            segment_structure._value = []
            return

        # Anything else takes the default of its first declared type.
        segment_structure._value = [(
            null_default_value(column_types[0] if len(column_types) > 0 else Any),
            ValueFormatter.DEFAULT_EMPTY_FORMATTER
        )]

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> VALUE EXPRESSION SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> Parse the right hand side of one declaration and push it into the value stack.
    #
    # CODE SEGMENT PART START.

    def _apply_value_expression(self,
                                segment_structure: ConfigurationDataStandaloneSegmentStructure,
                                value_string_part: str,
                                value_checker:     DatabasesSegmentValueChecker) -> None:
        """
        Parse a value expression and store it inside the segment.

        :param segment_structure: ConfigurationDataStandaloneSegmentStructure
        :param value_string_part: str                        Raw right hand side text.
        :param value_checker: DatabasesSegmentValueChecker    Type aware value parsers.
        :return: None
        """
        # Grammar.bnf: 'DEFAULT expr' takes the value unconditionally (it is also the fall back
        # of 'COMPARE DEFAULT'), so the keyword is simply stripped away here.
        leading_words: list[str] = value_string_part.strip().split(None, 1)
        if leading_words and leading_words[0].lower() == keyword.ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_DEFAULT:
            value_string_part = leading_words[1] if len(leading_words) > 1 else ""

        # Grammar.bnf: 'CALL ...' invokes the built in namespaces and belongs to the dynamic
        # CONVERSION support, which is still unimplemented (see `_data_load_conversion` and
        # src/parsefunc/execute.py). Fail loudly instead of hiding it behind a generic message.
        if leading_words and leading_words[0].lower() == keyword.ConfigurationDataExecutiveKeyword.EXECUTIVE_KEYWORD_CALL:
            raise NotImplementedError(
                "CALL is not supported yet: the dynamic CONVERSION executive "
                "(src/parsefunc/execute.py) is still empty."
            )

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
                try:  # Load into the normal mode.
                    inner_end: int = self._find_matching_brace_static(value_string_part, inner_brace_idx)
                    inner_content: str = value_string_part[inner_brace_idx + 1: inner_end]
                    child_statements: list[str] = self._split_top_level_statements_static(inner_content)
                    child_dictionary: dict[str, ConfigurationDataStandaloneSegmentStructure] = {}
                    self._data_load_databases(child_statements, child_dictionary)
                    segment_structure._value = [(child_dictionary, ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

                # Fallback: return an empty dictionary.
                except SyntaxError:
                    segment_structure._value = [({}, ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

            # no inline block — treat as empty dict.
            else:
                segment_structure._value = [({}, ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

            return

        # CODE SEGMENT PART END.
        # endregion
        #
        # ----- SEPARATING LINE -----
        #
        # IDENTIFICATION SEGMENT PART. TO >>> LIST PARSER SEGMENT.
        #
        # region
        # INTRODUCE SENTENCE.
        # -> Tables are loaded row by row, see `_data_load_table`.
        #
        # CODE SEGMENT PART START.

        if segment_structure.probable_type[1] == TypeExplainFormatter.LIST_TYPE_EXPLAIN:
            store_start_index, store_end_index = brackets_edge_index_checker(
                dat_info_string=value_string_part,
                right_move=0,
                left_bracket='[',
                right_bracket=']',
                string_ignore=True
            )

            # Start to list the element.
            segment_structure._value = [(row_item, ValueFormatter.DEFAULT_EMPTY_FORMATTER) for row_item in self._data_load_table(
                                            value_string_part[store_start_index + 1:store_end_index],
                                            segment_structure.probable_type[0],
                                            segment_structure.changeable
                                        )]
            return

        # CODE SEGMENT PART END.
        # endregion
        #
        # ----- SEPARATING LINE -----
        #
        # IDENTIFICATION SEGMENT PART. TO >>> NORMAL VALUE CHECK SEGMENT.
        #
        # region
        # INTRODUCE SENTENCE.
        # -> Everything else falls back to the type driven parsers.
        #
        # CODE SEGMENT PART START.

        if segment_structure.probable_type[1] == TypeExplainFormatter.DEFAULT_TYPE_EXPLAIN:
            for type_item in segment_structure.probable_type[0]:
                parser_func = value_checker.auto_check(getattr(type_item, "__name__", ""))
                if parser_func is not None:
                    segment_structure._value = parser_func(value_string_part, self._string_memory)
                    break

            # Single simple type, parse RHS. The string saving memory has to be handed over so a
            # quoted literal (ANYTHING and friends) consumes its own entry instead of leaving it
            # behind for the next statement.
            else:
                ldr_value: Any = complex_data_type_checker(value_string_part, self._string_memory)[0]
                segment_structure._value = [(ldr_value, ValueFormatter.DEFAULT_EMPTY_FORMATTER)]

            return

        # Or anything else, means that this is an unknown signal, we need to raise the Exception.
        raise TypeError(f"Unsupported signal: {segment_structure.probable_type[1]}")

        # CODE SEGMENT PART END.
        # endregion

    def _data_load_table(self, load_data_string: str, table_type: list[type], father_mutable: bool) -> list[Any]:
        """
        Load one `[...]` table literal into a list of rows.

        Two shapes are legal, exactly as Grammar.bnf describes them:
            [TABLE<INT, STR>] = [1, "a", 2, "b"]                 -> flat cycling over the columns
            [TABLE<INT, STR>] = [(1, "a"), (2, "b")]             -> parenthesised rows

        Each returned row is a plain list holding one value per column, so the whole table always
        follows the declared signature. It used to return half-built segment structures, drop
        every nested row and blow up with IndexError as soon as there were more elements than
        declared columns.

        :param load_data_string: str            Inner text of the table literal.
        :param table_type: list[type]           Declared column signature.
        :param father_mutable: bool             changeable flag inherited by every row.
        :return: list[Any]
        """
        final_saving_list: list[Any] = []

        if load_data_string.strip() == "":
            return final_saving_list

        value_checker: DatabasesSegmentValueChecker = DatabasesSegmentValueChecker(None, None)
        flat_index:    int = 0

        for raw_element in split_top_level_string(load_data_string, ","):
            element: str = raw_element.strip()
            if element == "":
                continue  # Tolerate the trailing comma allowed by Grammar.bnf.

            # A parenthesised group is one full row, anything else is a single column chunk.
            if element.startswith("(") and element.endswith(")"):
                column_items: list[str] = split_top_level_string(element[1 : -1], ",")
                if len(column_items) != len(table_type):
                    raise SyntaxError(
                        f"Table row {element!r} carries {len(column_items)} value(s) "
                        f"but {len(table_type)} column(s) were declared."
                    )
            else:
                column_items = [element]

            row_values: list[Any] = []
            for column_item in column_items:
                row_values.append(
                    self._load_table_cell(
                        column_item=column_item,
                        table_type=table_type,
                        flat_index=flat_index,
                        value_checker=value_checker,
                        father_mutable=father_mutable,
                    )
                )
                flat_index += 1

            final_saving_list.append(row_values)

        # Finally, we can return it.
        return final_saving_list

    def _load_table_cell(self,
                         column_item:    str,
                         table_type:     list[type],
                         flat_index:     int,
                         value_checker:  DatabasesSegmentValueChecker,
                         father_mutable: bool) -> Any:
        """
        Load a single cell of a table literal.

        :param column_item: str    Raw cell text (still with its quotes on).
        :param table_type: list[type]     Declared column signature.
        :param flat_index: int     Running element counter, used by flat tables.
        :param value_checker: DatabasesSegmentValueChecker
        :param father_mutable: bool
        :return: Any
        """
        cell_text: str = column_item.strip()

        # A list column is a nested table, so the whole content recurses into another table.
        column_type: Any = table_type[flat_index % len(table_type)]
        if isinstance(column_type, list):
            if cell_text.startswith("["):
                cell_text = cell_text[1 : ]  # noqa
            if cell_text.endswith("]"):
                cell_text = cell_text[ : -1]  # noqa
            return self._data_load_table(cell_text, column_type, father_mutable)

        # NULL inside a table keeps the column's default value.
        if cell_text.lower() == keyword.ConfigurationStatusExecutiveKeyword.STATUS_EXEC_KEYWORD_NULL:
            return null_default_value(column_type)

        # Strings were lifted into the saving memory up-front, so take the decoded content from
        # there instead of re-reading the raw (still escaped) text.
        if len(cell_text) >= 2 and cell_text[0] == '"' and cell_text[-1] == '"':
            return take_saved_string(self._string_memory, "table string value")

        parser_method: Any = value_checker.auto_check(getattr(column_type, "__name__", ""))

        # Anything else, we can just start the normal checking.
        if parser_method is None:
            return complex_data_type_checker(cell_text)[0]

        return evaluate_stack(parser_method(cell_text, self._string_memory))

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

                # Clean the keyword buffer: it used to keep the text read between two rules, so a
                # second rule such as `LIMIT(...), REGULAR(...)` was matched as one unknown name.
                temp_string = ""

                # Finally, jump out to the next index.
                extension_index = extend_end_index + 1

            # Or anything else, just increase the index.
            else:
                # Separators between two rules (", ") are dropped instead of being glued onto the
                # next keyword, which used to produce names such as ", regular".
                if extension_char in ",; \t" and temp_string.strip() == "":
                    extension_index += 1
                    continue

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


# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT END.
# endregion
#
# ----- SOURCE END -----
