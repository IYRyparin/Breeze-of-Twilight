"""
日志记录器\n
critical日志: 主要用于记录发生的程序报错或者连接中断等会直接导致进程结束的问题。
error日志: 主要用于记录发生的错误信息导致程序不得不跳过该段代码的情况。
warning日志: 主要用于记录运行时出现的部分问题，起到提示或者表明需要运行其他代码尝试解决，这些问题一般不会影响到程序的运行。
information日志: 就是信息记录，表明程序运行到了哪一个步骤。
success日志: 就是information日志下的一个子类，表明任务步骤已经成功完成。
debug日志: 详细记录每一段代码的运行情况，这个就是开发时为了直观追踪哪里报错设置的，虽然我也不着地有什么用。
initialize日志: 同样也是information日志下的一个子类，主要是启动时输出，没什么用。
control日志: 记录用户在界面上的操作。
这里原先是使用列表进行操作的，不过考虑到内存问题，这里准备改成重定向输出到指定日志文件。
我的手好欠……致未来的我：代码能跑就不要乱动了，谢绝重构！
"""

import time
import inspect
from typing import Callable, Optional


class LogCatalogue(object):
    def __init__(self,
                 configures: Optional[dict]         = None,
                 simple: Optional[bool]             = False,
                 pid: Optional[str]                 = None,
                 writing_file_path: Optional[str]   = None,
                 writing_file_encode: Optional[str] = "utf-8") -> None:
        """
        :param configures: dict   Configures dict of build log's configs quickly.
        :param simple: bool   Start simple log, this will clear many messages information.
        :param pid: str   Thread's pid which using this class, you can ignore it if you don't need it.
        :return: None
        """
        self.simple = simple
        self.process_pid = pid
        if writing_file_path is not None:
            self.temp_file_path = (writing_file_path, writing_file_encode)
            self.writing_file_path = open(writing_file_path, "a+", encoding=writing_file_encode)
            self.writing_file_path.write("[=======================[LOG CATALOGUE WITH AUTOMATION WEBSPIDER]====================]\n")
            self.writing_file_path.write(f"[===============[TIME: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]===============]\n")
            self.writing_file_path.flush()
        else:
            self.writing_file_path = self.temp_file_path = None

        if configures is None or "view_logs" not in configures.keys():  # maybe sometimes we forget or don't need to insert the config dict
            self.configs = {
                "stack": False,
                "critical": True,
                "warning": True,
                "error": True,
                "information": True,
                "control": False,
                "success": True,
                "debug": False,
                "initialize": False,
                "label": ("\tFILE: ", "\tLINE: ", "\tFUNCTION: "),
            }
        else:
            self.configs = configures['view_logs']

    def print_and_write(self, msg: Optional[str]) -> None:
        """
        Simple print function in here.
        :param msg: str   message string which will be printed into the terminal.
        :return: None
        """
        print(msg)

        # write the message into the file.
        if self.writing_file_path is not None:
            self.writing_file_path.write(msg + "\n")
            self.writing_file_path.flush()

    def stop_logging(self) -> bool:
        try:
            self.writing_file_path.close()
            self.writing_file_path = None
            return True

        except Exception as e:
            self.critical(f"\033[31mFailed to stop logging! {str(e)}!\033[0m")
            return False

    def continue_logging(self) -> bool:
        try:
            self.writing_file_path = open(self.temp_file_path[0], "a+", encoding=self.temp_file_path[1])
            return True

        except Exception as e:
            self.critical(f"\033[31mFailed to continue logging! {str(e)}!\033[0m\033[0m")
            return False

    def critical(self, msg: Optional[str]) -> None:  # 严重错误类别日志
        """

        :param msg: Optional[str]   message string which will be printed into the terminal.
        :return: None
        """
        if self.configs['critical']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:  # 由于栈输出十分耗时，所以这里引入了一个条件判断。
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[41m!\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{time}][\033[41mCRITICAL\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def warning(self, msg: Optional[str]) -> None:  # 警告类别日志
        """

        :param msg: Optional[str]   message string which will be printed into the terminal.
        :return: None
        """
        if self.configs['warning']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[33m!\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[33mWARNING\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def error(self, msg: Optional[str]) -> None:  # 错误类别日志
        if self.configs['error']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[31m-\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[31mERROR\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def information(self, msg: Optional[str]) -> None:  # 信息类别日志
        if self.configs['information']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[34m*\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[34mINFORMATION\033[0m]\t{msg} {stack}")
        else:
            pass

    def debug(self, msg: Optional[str]) -> None:  # 调试类别日志
        if self.configs['debug']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[1m.\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[1mDEBUG\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def success(self, msg: Optional[str]) -> None:  # 运行成功类别日志，从这里开始属于其他类型了。
        if self.configs['success']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[32m+\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[32mSUCCESS\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def control(self, msg: Optional[str]) -> None:
        if self.configs['control']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[32m%\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[32mCONTROL\033[0m]\t\t{msg} {stack}")
        else:
            pass

    def initialize(self, msg: Optional[str]) -> None:  # 初始化类别日志
        if self.configs['initialize']:
            times, stack, it_ = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), "\033[32m", iter(self.configs['label'])
            if self.configs['stack']:
                for i in inspect.stack()[1][1:4]:
                    stack += next(it_) + str(i)
            stack += "\033[0m"
            self.print_and_write(f"[\033[1m@\033[0m] {msg}" if self.simple else f"{check_print(self.process_pid)}[{times}][\033[1mINITIALIZE\033[0m]\t{msg} {stack}")
        else:
            pass

    def __del__(self) -> None:  # close the class.
        if self.writing_file_path is not None:
            self.writing_file_path.write("[=====================================[LOG ENDS]=====================================]")
            self.writing_file_path.close()


class EmptyLogCatalogue(object):
    """
    This is an empty catalogue.
    Do not use this class directly, only you don't want any output and don't want to remove the code from this control part.
    """
    def __init__(self, configures=None, simple=False, pid=None): pass
    def critical(self, msg): pass
    def error(self, msg): pass
    def warning(self, msg): pass
    def information(self, msg): pass
    def debug(self, msg): pass
    def success(self, msg): pass
    def control(self, msg): pass
    def initialize(self, msg): pass


def status_print(status: bool) -> str:
    spawn_spawn = "\033[32m" if status else "\033[31m"
    return f"{spawn_spawn}{"True" if status else "False"}\033[0m"


check_print: Callable[..., str] = lambda message: f"[{message}]" if message is not None else ""
