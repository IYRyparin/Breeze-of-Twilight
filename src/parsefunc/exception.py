import ctypes
from typing import Final, Optional

from src.parseutil.signal import ErrorCodeFormatter


# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL EXCEPTION. TO >>> BASE EXCEPTION CLASS PACKAGE.
#
# INTRODUCE SENTENCE.
# -> Those class defines the basic exception for the BOT, and it will be used in the BOT to raise some exception when something goes wrong.
# -> Furthermore, it can also be used to catch some exception when something goes wrong, and it can also be used to print some exception when something wrong.
# -> Let me add something, because all the custom exception classes inherits from the base exception class, so you can use this to catch all of them.
#
# GLOBAL CODE SEGMENT START.

# ----- CLASS BASIC INTRODUCE -----
# -> Well, This is the basic exception for all of them which will be used to define other exception.
# -> If you're too lazy to catch the exception, just use this can catch all of them.
# -> Well...Why I don't use the default exception class? IDK.
# ----- INTRODUCE END -----
#
# START OF THE SOURCE CODE.

class BOTBaseException(Exception):
    def __init__(self,
                 # +--------+---------------------+
                 # |  NAME  |        TYPE         |
                 # +--------+---------------------+
                 message:    Optional[str],
                 error_code: Optional[ctypes.c_uint8],
                 error_line: Optional[int],
                 error_part: Optional[str],
                 error_type: Optional[str],
                 error_file: Optional[str]
                 # +--------+---------------------+
                 ) -> None:
        super(BOTBaseException).__init__(message, error_code, error_line, error_part, error_type, error_file)

        # initialize the basic value in the args.
        # +--------------+---------------------+-------------+-------------------------+----------------+
        # |    NAME      |        TYPE         |    VALUE    |      REQUIREMENT        |     OTHER      |
        # +--------------+---------------------+-------------+-------------------------+----------------+
        self._message:    Final[str]            = message     if message is not None     else "N/A"
        self._error_code: Final[ctypes.c_uint8] = error_code  if error_code is not None  else ErrorCodeFormatter.DEFAULT_CRITICAL_QUITTING_ERROR
        self._error_line: Final[int]            = error_line  if error_line is not None  else -0x01
        self._error_part: Final[str]            = error_part  if error_part is not None  else "N/A"
        self._error_type: Final[str]            = error_type  if error_type is not None  else "N/A"
        self._error_file: Final[str]            = error_file  if error_file is not None  else "N/A"
        # +--------------+---------------------+------------+-------------------------+----------------+

        # push in the basic exception message.
        self.message_basic_with: str = "CRITICAL BASE EXCEPTION"

    def __str__(self) -> str:
        """
        When try to print the exception message,
        Those message will be print out.
        :return: str
        """
        return \
        f"""{self.message_basic_with}
         -> ERROR MESSAGE: {self._message}
         -> ERROR CODE: {self._error_code.value}
        When load the configuration, An error has been occurred from:
         -> File: {self._error_file}
         -> Line: {self._error_line}
         -> Part: {self._error_part}
         -> Type: {self._error_type}
        """

    def __getitem__(self, item: int) -> str:
        """
        When define this function, you don't need to extract the error's information with compile string.
        It includes seven different items, all in the message which printed out. You can use an int value to extract it.
        :param item: int   The message's information which you want to get.
        :return: str
        """
        match item:
            case 0: return str(self.message_basic_with)
            case 1: return str(self._message)
            case 2: return str(self._error_code.value)
            case 3: return str(self._error_file)
            case 4: return str(self._error_line)
            case 5: return str(self._error_part)
            case 6: return str(self._error_type)
            case _: raise IndexError("Index must be the number in 0 ~ 6")

# END OF THE SOURCE CODE.

# ----- CLASS BASIC INTRODUCE -----
# -> When you try to load a file with error syntax or some part which parser couldn't understand's words, it will be occurred.
# ->
# ->
# ----- INTRODUCE END -----
# region
# START OF THE SOURCE CODE.


class BOTDecodeSyntaxException(BOTBaseException):
    def __init__(self,
                 # +--------+---------------------+
                 # |  NAME  |        TYPE         |
                 # +--------+---------------------+
                 message:    Optional[str],
                 base_code:  Optional[list[str]],
                 error_type: Optional[str],
                 error_part: Optional[str],
                 error_file: Optional[str],
                 # +--------+---------------------+
                 ) -> None:

        # ----- BASIC VALUE ENVIRONMENT SETTING START -----
        # region
        #
        # INTRODUCE SENTENCE.
        # -> I'm afraid that I don't need to waste my time on it.
        # -> Just to initialize some symbol which can show the identification of the exception.
        # -> Nothing at all, just do it!
        #
        # DATA SEGMENT START.

        super().__init__(
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
            # |  NAME   |  EXCEPTION BASE INFORMATION       |    VALUE REQUIREMENTS                                |    OTHER       |
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
            message     = message                               if message is not None                              else "N/A",
            error_code  = ErrorCodeFormatter.FILE_DECODE_ILLEGAL_SYNTAX,
            error_type  = f"Not supported {error_type} type",
            error_part  = error_part                            if error_part is not None                           else "N/A",
            error_line  = base_code.index(error_part)           if base_code is not None and error_part is not None else -1,
            error_file  = error_file                            if error_file is not None                           else "N/A"
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
        )

        # initialize the basic exception message.
        self.message: Final[str] = message if message is not None else "N/A"
        self.message_basic_with: Final[str] = "CRITICAL FAILED: DECODE ERROR"

        # DATA SEGMENT END.
        #
        # ----- BASIC VALUE ENVIRONMENT SETTING END. -----
        #
        # endregion


# END OF THE SOURCE CODE.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- CLASS BASIC INTRODUCE -----
# ->
# ->
# ->
# -----INTRODUCE END -----
# region
# START OF THE SOURCE CODE.

class BOTEncodeException(BOTBaseException):
    def __init__(self,
                 # +--------+---------------------+
                 # |  NAME  |        TYPE         |
                 # +--------+---------------------+
                 message:     Optional[str]
                 # +--------+---------------------+
                 ) -> None:
        super().__init__(
            # push in the information to base exception.
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
            # |  NAME   |  EXCEPTION BASE INFORMATION       |    VALUE REQUIREMENTS                                |    OTHER       |
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
            message
            # +---------+-----------------------------------+------------------------------------------------------+----------------+
        )

        # initialize the basic exception information.
        self.message: Final[str] = message if message is not None else "N/A"
        self.message_basic_with = "CRITICAL FAILED: ENCODE ERROR"

# END OF THE SOURCE CODE.
# endregion
#
# ----- SEPARATING LINE -----
#
#
#
#
#

class BOTDecodeException(BOTBaseException):
    ...

# END OF THE SOURCE CODE.
# endregion
#
# ----- SEPARATING LINE -----
#
#
#
#
#
#

class BOTInvalidExecutiveException(BOTBaseException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
        )

# END OF THE SOURCE CODE.
# endregion
#
# ----- SEPARATING LINE -----
#
# GLOBAL CODE SEGMENT END.
#
# IDENTIFICATION END.
# endregion
#
# ----- SOURCE END -----
