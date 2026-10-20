from queue import Queue
from typing import Any

from src.v10.struct import kword as keyword
from src.v10.struct.char import *
from src.v10.struct.signal import ValueFormatter
from src.v10.interface.caller import CallSegmentParser
from src.v10.valchk.strchk.contain import brackets_edge_index_checker
from src.v10.valchk.strchk.strtake import take_saved_string


class FormatChecker(object):
    def __init__(self,
                 value:         str,
                 queue_loader:  Queue[tuple[str, int]],
                 is_conversion: bool                   = False) -> None:
        """
        Check and format the origin value's string to the list.
        :param value: Value's origin string.
        :param queue_loader: A queue which saved the string.
        :param is_conversion: It is a conversion value or not.
        """
        self._value:         str                   = value
        self._final_list:    list[tuple[Any, int]] = []
        self._pointer:       int                   = 0
        self._queue_loader:  Queue[tuple[str, int]] = queue_loader
        self._value_length:  int                   = len(value) - 1
        self._is_conversion: bool                  = is_conversion
        self._temp_queue:    Queue[str]            = Queue()

    # IDENTIFICATION SEGMENT PART. TO >>> NORMAL INTERFACE SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def start_run(self) -> None:
        self._break_the_value()

    def get_final_list(self) -> list[tuple[str, int]]:
        return self._final_list

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> ASSIST FUNCTION SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _input_list(self, value: str, explain: int, clean_queue: bool = True) -> None:
        if value != "":
            if clean_queue:
                copy_value: str = ""
                while self._temp_queue.qsize() > 0:
                    copy_value += self._temp_queue.get()
                copy_value += value
            self._final_list.append((value, explain))

    @staticmethod
    def _check_is_keyword(value: str, load_from_queue: bool = False) -> bool:
        final_check_signal: bool = False
        if all(x in LEGAL_STRING_WORD[:-12] + "-_" for x in value) and value != "":  # All word is in the English word.
            for local_package in list(filter(lambda x: x.startswith("Configuration"), dir(keyword))):
                if value in getattr(keyword, local_package)().__list__():
                    final_check_signal = True
        return final_check_signal and not load_from_queue

    @staticmethod
    def _is_special_keyword_sentence(value: str) -> bool:
        return value in keyword.ConfigurationValueRequireSentencesKeyword().__list__()

    def _special_parse_function(self, value: str) -> Any:
        match value:
            case keyword.ConfigurationValueRequireSentencesKeyword.FORMAT:
                return self._string_format_keyword_search
            case keyword.ConfigurationValueRequireSentencesKeyword.CALL:
                return self._string_call_keyword_search
            case keyword.ConfigurationValueRequireSentencesKeyword.TO:
                return self._to_sentence_search
            case keyword.ConfigurationValueRequireSentencesKeyword.SUMMARY:
                return self._sum_sentence_search
            case _:
                raise NotImplementedError("Not supported keyword name.")

    def _search_next_legal_char(self, jump: frozenset[str]) -> int:
        """
        This function is used to jump out the char in sentence which useless character.
        For example, when you want to jump the space in the sentence,
        it will return a pointer with the char which is not space after the pointer in "self" pointer.
        :param jump: frozenset[str]   Which char you want to jump out.
        :return: int   Final pointer.
        """
        pointer: int = self._pointer
        while pointer < self._value_length and self._value[pointer] in jump:
            pointer += 1
        return pointer

    def _search_next_legal_value(self, end_signal: frozenset[str]) -> tuple[str, bool]:
        """
        This function is used to check the next value part until find the end signal.
        However, if the value is string type, it will use special method to get the value from the queue.
        :param end_signal: frozenset[str]   Which char you want to jump out.
        :return: tuple[str, bool]   Final value and a flag indicating if the value came from the queue.
        """
        string_signal: bool = False
        value_loader:  str  = ""
        from_queue:    bool = False
        search_index:  int  = 0

        # Start the loop to search the default value.
        for search_index, search_char_item in enumerate(self._value[self._pointer:]):
            if search_char_item == "\"":
                string_signal = not string_signal  # Change the signal to show that we are in or out of the string.

                # For string type, we need to use special method to do it.
                if not string_signal and self._queue_loader is not None:
                    value_loader = take_saved_string(self._queue_loader)[0]

            # Check the end signal in here.
            elif not string_signal and search_char_item in end_signal:
                self._pointer += search_index
                return value_loader, from_queue

            # Add the char in here.
            else:
                value_loader += search_char_item

        # For stable, we can put a default return in here.
        self._pointer += search_index
        return value_loader, from_queue

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> VALUE BREAKING SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # -> In here, is the function which start to break and change the value.
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _break_the_value(self) -> None:  # If you can read the history of the git, you'll know how much time I have rewritten this.
        """
        This function is used to break the origin string into the list.
        For example, like: "1 + 3 + 5", we'll break it into ['1', '+', '3', '+', '5'].
        All the item is tuple value, first is the value with string type.
        And second is the signal which describe the type of the value.
        :return: None
        """
        temp_saving_string: str        = ""
        string_signal:      bool       = False

        # Start the loop, search the value and merge it into the final list.
        while self._pointer < self._value_length:
            char:        str  = self._value[self._pointer]
            add_it:      bool = True
            increase_it: bool = True
            load_queue:  bool = False

            # Check the string signal, load string from safety queue.
            if char == "\"":
                string_signal = not string_signal
                if not string_signal:
                    temp_saving_string = take_saved_string(self._queue_loader)[0]
                    load_queue = True

                add_it = False

            # Drop out the blank char in here.
            if char == " " and not string_signal:
                if temp_saving_string != "":   # Ignore the empty method.
                    if self._check_is_keyword(temp_saving_string, load_queue) and self._is_special_keyword_sentence(temp_saving_string):
                        self._special_parse_function(temp_saving_string)()
                    else:
                        self._temp_queue.put(temp_saving_string)
                    temp_saving_string = ""
                add_it = False

            # Check the bracket's edge signal.
            if char in BRACKET_CHAR and not string_signal:
                value_signal: int = ValueFormatter.KEYWORD_SIGNAL_FORMATTER if self._check_is_keyword(temp_saving_string, load_queue) else ValueFormatter.DEFAULT_EMPTY_FORMATTER
                self._input_list(temp_saving_string, value_signal)
                self._input_list(char, ValueFormatter.OPERATION_SIGNAL_FORMATTER)
                temp_saving_string = ""
                add_it = False

            # End point signal, start to merge the value into the list.
            if char in CALCULATE_CHAR and not string_signal:
                value_signal: int = ValueFormatter.KEYWORD_SIGNAL_FORMATTER if self._check_is_keyword(temp_saving_string, load_queue) else ValueFormatter.DEFAULT_EMPTY_FORMATTER
                if value_signal == ValueFormatter.KEYWORD_SIGNAL_FORMATTER and self._is_special_keyword_sentence(temp_saving_string):
                    self._special_parse_function(temp_saving_string)()  # Call the target function which parse the special sentence.
                else:
                    self._input_list(temp_saving_string, value_signal)
                temp_saving_string = ""

                # Check the operation signal's edge, merge full operation signal.
                while self._pointer < self._value_length and self._value[self._pointer] in CALCULATE_CHAR:
                    temp_saving_string += self._value[self._pointer]
                    self._pointer += 1

                # Input the value into the final list, and then we can increase the pointer and just continue.
                self._input_list(temp_saving_string, ValueFormatter.OPERATION_SIGNAL_FORMATTER)
                temp_saving_string = ""
                add_it = False
                increase_it = False

            # Append the char into the value. How I build this shit?
            if not string_signal and add_it:
                temp_saving_string += char
            if increase_it:
                self._pointer += 1

        # Prepare for the last part of the char.
        # During the last, we can ignore some rule, but we also need to care about the trouble in here.
        if self._pointer == self._value_length:  # Sometimes it may have special rule's keyword in the last, if we ignore this sentence, we may repeat the value.
            char: str = self._value[-1]
            if char == "\"" and self._queue_loader is not None:
                self._input_list(*take_saved_string(self._queue_loader))

            # Not the string, we can try to match the value in here.
            temp_saving_string += char.strip()
            signal_payload: int = ValueFormatter.KEYWORD_SIGNAL_FORMATTER if self._check_is_keyword(temp_saving_string, False) else ValueFormatter.DEFAULT_EMPTY_FORMATTER

            # Check is special keyword or not.
            if signal_payload == ValueFormatter.KEYWORD_SIGNAL_FORMATTER and self._is_special_keyword_sentence(temp_saving_string):
                match temp_saving_string:
                    case keyword.ConfigurationValueRequireSentencesKeyword.FORMAT:
                        self._string_format_keyword_search()
                    case _:
                        if char in BRACKET_CHAR:
                            self._input_list(temp_saving_string[:-1], ValueFormatter.DEFAULT_EMPTY_FORMATTER)
                            self._input_list(char, ValueFormatter.OPERATION_SIGNAL_FORMATTER)
                        else:
                            self._input_list(temp_saving_string, ValueFormatter.DEFAULT_EMPTY_FORMATTER)

            # Not the special keyword, merge it as normal value.
            else:
                if char in BRACKET_CHAR:
                    self._input_list(temp_saving_string[:-1], signal_payload)
                    self._input_list(char, ValueFormatter.OPERATION_SIGNAL_FORMATTER)
                else:
                    self._input_list(temp_saving_string, signal_payload)

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> SPECIAL SENTENCE PARSER SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _string_format_keyword_search(self, *_) -> None:
        """
        This function is used to search and merge the "format" sentence.
        Under normal conditions, this sentence has two probable.
        - "format default XXX", means there has default value when developer never format the sentence.
        - "format" solo, means default value is NULL.
        :return: None
        """
        self._pointer = self._search_next_legal_char(frozenset({" "}))

        # Start to check the default value and replace the string in here.
        try:
            if self._pointer == self._value_length:  # Close to the edge, means nothing we need to care, just throw the exception
                raise IndexError

            # Mark down the default keyword, start to search and check the default value.
            elif "".join(self._value[self._pointer: self._pointer + 7]) == keyword.ConfigurationValueRequireSentencesKeyword.DEFAULT:
                self._pointer += 7  # Jump to the default value's start state.
                self._pointer = self._search_next_legal_char(frozenset({" "}))
                get_value, queue_load_signal = self._search_next_legal_value(frozenset(set(CALCULATE_CHAR).union({" "})))
                signal_payload: int = ValueFormatter.KEYWORD_MUTABLE_SIGNAL_FORMATTER if self._check_is_keyword(get_value, queue_load_signal) else ValueFormatter.DEFAULT_EMPTY_MUTABLE_FORMATTER
                self._input_list(get_value, signal_payload)

            # Not the "DEFAULT" keyword, we can follow to next part.
            else:
                raise IndexError

        # Cause the exception, means there don't have any defined default value, we can set it with null
        except IndexError:
            self._input_list(keyword.ConfigurationValueReplacerKeyword.NULL, ValueFormatter.KEYWORD_MUTABLE_SIGNAL_FORMATTER)

    def _string_call_keyword_search(self, *_) -> None:
        """
        This function is used to search and merge the "call" sentence.
        Call sentence is used to call the package name and return the conversion value in here.
        :return: None
        """
        temp_saving_string: str
        self._pointer = self._search_next_legal_char(frozenset({" "}))

        # Start to search the package name in here.
        for sentence_index, sentence_char in enumerate(self._value[self._pointer:]):
            if sentence_char in "<([{":
                bracket_end_index: int = brackets_edge_index_checker(
                    dat_info_string=self._value,
                    right_move=self._pointer,
                    left_bracket="(",
                    right_bracket=")"
                )[1]
                temp_saving_string = self._value[self._pointer: bracket_end_index]
                break

            # No brackets in here, means no parameter, we can just input the function and return it.
            elif sentence_char in CALCULATE_CHAR or sentence_char == " ":
                temp_saving_string = self._value[self._pointer: sentence_index]
                break

        # Crash on the edge, we need some little check.
        else:
            temp_saving_string = self._value[self._pointer:]

        # Merge the value, check the function and add it to the list.
        call_segment: CallSegmentParser = CallSegmentParser(temp_saving_string)
        return_value, add_index = call_segment.search_package(temp_saving_string)
        self._input_list(return_value, ValueFormatter.DEFAULT_EMPTY_FORMATTER)
        self._pointer += add_index

    def _to_sentence_search(self, *_) -> None:
        first_value: str = self._temp_queue.get()
        self._pointer = self._search_next_legal_char(frozenset({" "}))  # Jump out the blank part.

    def _sum_sentence_search(self, *_) -> None:
        ...

    # CODE SEGMENT PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # IDENTIFICATION SEGMENT PART. TO >>> SPECIAL KEYWORD ASSIST CELL SEGMENT.
    #
    # region
    # INTRODUCE SENTENCE.
    # ->
    # ->
    # ->
    #
    # CODE SEGMENT PART START.

    def _to_sentence_cell_search(self, start: str, end: str) -> None:
        ...

    # CODE SEGMENT PART END.
    # endregion
