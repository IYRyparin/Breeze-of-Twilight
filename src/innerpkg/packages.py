# -*- INNER PACKAGE -*-

import dataclasses
import platform
import threading
import netifaces
import datetime
import socket
import struct
import uuid
import time
import re
import os
from functools import lru_cache
from typing import Final, Any

# ----- CONSTANT START -----
# ENVIRONMENT GLOBAL DATA SEGMENT START

MAX_CACHE_VALUE: Final[int] = 256
CHECKING_DICTIONARY: Final[dict[str, Any]] = {
    # +---------------------------+---------------------------------------+
    # |           KEY             |                VALUE                  |
    # +---------------------------+---------------------------------------+
    # Those value is used to check the method's name and return the correct value. Because those method is used by configuration, so I need to make sure that those method is correct and can be called by configuration.
    "GetCurrentTime":               lambda: get_current_time(),
    "GetCurrentYear":               lambda: get_current_time("year"),
    "GetCurrentMonth":              lambda: get_current_time("month"),
    "GetCurrentDay":                lambda: get_current_time("day"),
    "GetCurrentHour":               lambda: get_current_time("hour"),
    "GetCurrentMinute":             lambda: get_current_time("minute"),
    "GetCurrentSecond":             lambda: get_current_time("second"),

    # Those value is used to check the method's name and return the correct value. Because those method is used by configuration, so I need to make sure that those method is correct and can be called by configuration.
    "GetLocalMachineIPV4":          lambda: get_system_ipv4(),
    "GetLocalMachineIPV6":          lambda: get_system_ipv6(),
    "GetLocalMachineMask":          lambda: get_system_mask(),
    "GetLocalMachineGateway":       lambda: get_system_gateway(),

    # Those value is used to check the method's name and return the correct value. Because those method is used by configuration, so I need to make sure that those method is correct and can be called by configuration.
    "GetLocalMachineMAC":           lambda: get_system_mac(),
    "GetLocalMachineName":          lambda: get_local_machine_name(),
    "GetLocalMachineFQDN":          lambda: get_local_machine_fqdn(),
    "GetLocalMachineSystemName":    lambda: get_local_machine_system_name(),
    "GetLocalMachineSystemVersion": lambda: get_local_machine_system_version(),
    "GetLocalMachineSystemRelease": lambda: get_local_machine_system_release(),
    # +---------------------------+---------------------------------------+
}

# ENVIRONMENT GLOBAL DATA SEGMENT END
# ----- CONSTANT END -----
#
# ----- SEPARATING LINE -----
#
# ----- SOURCE START -----
#
# region
# IDENTIFICATION GLOBAL FUNCTION. TO >>> CONFIGURATION USING FUNCTION.
#
# INTRODUCE SENTENCE.
# -> This file defines some read-only function which can be used in the configure file,
# -> You can use those function to get the basic information such as time, path, etc.
# -> But also, more function means more loopholes, so this configures language only support limited function.
# -> If you want more, I'm afraid that maybe you need to realize it by turing-complete program language rather than that.
#
# GLOBAL CODE SEGMENT START.

# ----- GET TIME SEGMENT -----
#
# region
# INTRODUCE SENTENCE.
# -> TODO: CALL BY SPECIAL VALUE: GetCurrentTime、GetCurrentYear、GetCurrentMonth、GetCurrentDay、GetCurrentHour、GetCurrentMinute、GetCurrentSecond
# -> Holy shit why I need to add those useless method's supported?
#
# DATA SEGMENT START.

@dataclasses.dataclass(frozen=True)
class GetCurrentTimeSignal(object):
    # +--------------------+------------+--------------------+
    # |        NAME        |    TYPE    |       VALUE        |
    # +--------------------+------------+--------------------+
    GET_DEFAULT_FULL_STRING: Final[str] = "default"
    GET_YEAR:                Final[str] = "year"
    GET_MONTH:               Final[str] = "month"
    GET_DAY:                 Final[str] = "day"
    GET_HOUR:                Final[str] = "hour"
    GET_MINUTE:              Final[str] = "minute"
    GET_SECOND:              Final[str] = "second"
    # +--------------------+------------+--------------------+

    @staticmethod
    def checking_method_string(method: str) -> str:
        """
        This is a simple part which can help you
        :param method: str   Configuration language's method name which call the read-only interface.
        :return: str
        """
        match method:
            case "GetCurrentTime": return GetCurrentTimeSignal.GET_DEFAULT_FULL_STRING
            case "GetCurrentYear": return GetCurrentTimeSignal.GET_YEAR
            case "GetCurrentMonth": return GetCurrentTimeSignal.GET_MONTH
            case "GetCurrentDay": return GetCurrentTimeSignal.GET_DAY
            case "GetCurrentHour": return GetCurrentTimeSignal.GET_HOUR
            case "GetCurrentMinute": return GetCurrentTimeSignal.GET_MINUTE
            case "GetCurrentSecond": return GetCurrentTimeSignal.GET_SECOND
            case _: raise TypeError(f"Unknown method type: {method}")

# DATA SEGMENT END.
#
# ----- SEPARATING LINE -----
#
# CODE SEGMENT START.

# @lru_cache(maxsize=MAX_CACHE_VALUE)  # Wny I cut out this? well...you know.
def get_current_time(part: str = "default") -> str:
    """
    This function returns the current time in local time. It is used by configuration's default function list: packages.
    When you only want a part of the time information, you can use this function to get it.
    For example, if you only want the year information, you can use "GetCurrentTime.year" to get it.
    Afterwords, if you only call this function without backwards, only use this function name just all.
    :param part: str    Which part of the time to return.
    :return: str
    """
    # +------------+------------+--------------------+
    # |    NAME    |    TYPE    |       VALUE        |
    # +------------+------------+--------------------+
    local_time:      Final[str] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    local_time_list: list[str]  = []
    # +------------+------------+--------------------+

    # ----- TIME CRACK FUNCTION PART -----
    # region
    # INTRODUCE SENTENCE.
    # -> Because it needed to support to get the part of the time, we need to use those codes to break the time's string.
    # -> I'm lazy to call the interface and get the system's time second time, so I break the string to do it.
    # -> WARNING: If you realize data without conversion type, it will note the time when read this file. If you want to get the converse time, please use "conversion<str>" to do it.
    #
    # TIME CRACK FUNCTION PART START.

    # crack the large time information.
    for time_item in local_time.split(" ")[0].split("-"):
        local_time_list.append(str(time_item))

    # crack the elaborate time information.
    for time_item in local_time.split(" ")[1].split(":"):
        local_time_list.append(str(time_item))

    # change value to tuple to keep value's safe, and delete useless value.
    local_time_tuple: Final[tuple[str, ...]] = tuple(local_time_list[0:6])
    del local_time_list, time_item

    # TIME CRACK FUNCTION PART END.
    # endregion
    #
    # ----- SEPARATING LINE -----
    #
    # ----- SPRIT COMPARE PART -----
    #
    # region
    # INTRODUCE SENTENCE.
    # -> From here, is the part which used to check the part's namespace and return the correct value.
    # -> When we need to get the part of the time, we can use this function to get it. For example, if you want to get the year information, you can use "GetCurrentTime.year" to get it.
    # -> Also, because the time's part is in the same order as the time's string, so we can use the index to get the correct value. For example, if you want to get the year information, you can use "GetCurrentTime.year" to get it, and because the year is in the first part of the time's string, so we can use index 0 to get it.
    #
    # SPRIT COMPARE PART START.

    match part:
        case "second": return local_time_tuple[5]
        case "minute": return local_time_tuple[4]
        case "hour": return local_time_tuple[3]
        case "day": return local_time_tuple[2]
        case "month": return local_time_tuple[1]
        case "year": return local_time_tuple[0]
        case _: return local_time

    # SPRIT COMPARE PART END.
    # endregion

# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- GET CURRENT NETWORK INFORMATION CODE SEGMENT -----
#
# region
# INTRODUCE SENTENCE.
# -> This part is used to get local system's basic information such as IP address, MAC address, etc.
# -> Because this part may cause security problem, you can terminate it when you don't want to use it.
#
# CODE SEGMENT START.

# TODO: CALL BY SPECIAL VALUE: GetLocalMachineIPV4
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_system_ipv4() -> str:
    """
    This function returns the system ipv4 address.
    It is used by configuration's default function list: packages.
    This part need your local system has connected to the internet. If not, it will return a default string value: "localhost".
    :return: str
    """
    # +----+----------------+-----------------------------------------------------+------------------------+
    # |NAME|      TYPE      |                           VALUE                     |         EXPLAIN        |
    # +----+----------------+-----------------------------------------------------+------------------------+
    sock:     socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)   # defines a socket session af first, but do nothing.
    # +----+----------------+-----------------------------------------------------+------------------------+

    # Start to get ip address.
    # This method exploit UDP protocol to get local ip, which build a UDP package and get IP from it.
    try:
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]

    # catch the error and return default value.
    except (socket.error, Exception):
        return "localhost"

    # At finally, close the session and delete useless value.
    finally:
        sock.close()
        del sock

    # return the value.
    return str(ip)


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineIPV6
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_system_ipv6() -> str:
    """
    This function returns the system ipv6 address.
    It is used by configuration's default function list: packages.
    This part need your local system has connected to the internet. If not, it will return a default string value: "localhost" in list.
    :return: str
    """
    # +------------+----------+------------+------------------------+
    # |    NAME    |   TYPE   |   VALUE    |         EXPLAIN        |
    # +------------+----------+------------+------------------------+
    ipv6_addresses: list[str] = []           # A multiple value which used to save local ip address.
    # +------------+------+------------+------------------------+

    try:  # build the compile string.
        ipv6_regex = re.compile(r'(([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){6}:[0-9a-fA-F]{1,4})|(([0-9a-fA-F]{1,4}:){5}(:[0-9a-fA-F]{1,4}){1,2})|(([0-9a-fA-F]{1,4}:){4}(:[0-9a-fA-F]{1,4}){1,3})|(([0-9a-fA-F]{1,4}:){3}(:[0-9a-fA-F]{1,4}){1,4})|(([0-9a-fA-F]{1,4}:){2}(:[0-9a-fA-F]{1,4}){1,5})|([0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6}))|(:((:[0-9a-fA-F]{1,4}){1,7}))')

        # List the address and find correct string.
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET6):
            if len(info[4][0]) >= 6 and len(str(ipv6_regex.match(info[4][0]))) > 1:  # noqa
                ipv6_addresses.append(info[4][0])

        # Delete useless value and return the address. Maybe you're questions that why I do this, because I want to use this method to practice myself.
        del info, ipv6_regex

        # If nothing in the list, return the default value.
        if len(ipv6_addresses) < 0:
            return "localhost"

        # On the other hand, return the last part of the interfaces. Typically, it is the correct address.
        return ipv6_addresses[0]

    # catch the potential exception and return the special error message.
    except (IndexError, socket.gaierror, Exception):
        return "localhost"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineMask
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_system_mask() -> str:
    """
    This function returns the system mask address.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: localhost.
    :return: str
    """
    try:  # start to get netmask.
        routing_nic_name = netifaces.gateways()['default'][netifaces.AF_INET][1]

        # list all interfaces to find target interface.
        for interface in netifaces.interfaces():
            if interface == routing_nic_name:
                return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']

        # find nothing, return error message.
        return "localhost"

    # catch the potential error and return the error message.
    except (TypeError, ValueError, Exception):
        return "localhost"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineGateway
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_system_gateway() -> str:
    """
    This function returns the system's network gate's address.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: localhost, to means get failed.
    :return: str
    """
    network_gate: str = "localhost"

    try:  # Get gateway from default router
        gateways = netifaces.gateways()
        default_gateway = gateways['default'][netifaces.AF_INET][0]

        # check the default value's type, make sure this is a string.
        if isinstance(default_gateway, str):
            network_gate = default_gateway

        # Delete useless value.
        del default_gateway, gateways

    # catch the exception and return the default value.
    except (TypeError, ValueError, Exception):
        network_gate = "localhost"

    # Delete useless value and return the gate's address.
    return network_gate

# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# ----- GET CURRENT MACHINE INFORMATION CODE SEGMENT -----
#
# region
# INTRODUCE SENTENCE.
# -> Those function is used to get local machine's basic information.
# -> Why those function is needed? Because some configuration may need to get the local machine's information to do some special configuration, such as get the mac address to do some special configuration.
# -> From those function, you can get the information such as local system's name, domain, mac address, etc.
#
# CODE SEGMENT START.

# TODO: CALL BY SPECIAL VALUE: GetLocalMachineMAC
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_system_mac() -> str:
    """
    This function returns the system mac address.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: localhost
    :return: str
    """
    try:  # Use uuid to get it.
        # +-------------+-----------+---------------------------+
        # |    NAME     |   TYPE    |           VALUE           |
        # +-------------+-----------+---------------------------+
        mac_address_tmp: Final[str] = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
        mac_address:     Final[str] = '-'.join([mac_address_tmp[ i : i + 2 ] for i in range(0, 11, 2)])

        # Delete the useless value and return the address
        del mac_address_tmp
        return mac_address

    # To make sure stable, catch the potential error and return the error information.
    except (TypeError, ValueError, Exception):
        return "localhost"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineName
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_local_machine_name() -> str:
    """
    This function returns the local machine name. It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: localhost
    :return: str
    """
    try:
        return socket.gethostname()

    # catch potential exception and return the error value.
    except (TypeError, ValueError, Exception):
        return "localhost"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineFQDN
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_local_machine_fqdn() -> str:
    """
    This function returns the local machine FQDN. It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: localhost
    :return: str
    """
    try:
        return socket.getfqdn()

    # catch potential exception and return the error value.
    except (TypeError, ValueError, Exception):
        return "localhost"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineSystemName
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_local_machine_system_name() -> str:
    """
    This function returns the local machine system name.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: Unknown
    :return: str
    """
    # +----------------+------------+--------------------+----------------------+
    # |    NAME        |   TYPE     |     VALUE          |    DESCRIPTION       |
    # +----------------+------------+--------------------+----------------------+
    linux_issue_file:   Final[str]  = "/etc/issue"        # The file's part which may save the release information of the system. But not all linux system has this file, so we need to check it.
    linux_release_file: Final[str]  = "/etc/release"      # The file's part which may save the release information of the system. But not all linux system has this file, so we need to check it.
    # +----------------+------------+--------------------+----------------------+

    # start to match and check basic system's type.
    match platform.system():
        case "Windows": return "Windows"
        case "Darwin":  return "MacOS"
        case "FreeBSD": return "FreeBSD"

        # Because Linux has too much type, so from here we need to check the information and return it.
        case _:  # At first, we need to start to check the file is in here or not.
            if os.path.isfile(linux_issue_file) and os.access(linux_issue_file, os.R_OK):  # check the issue file.
                with open(linux_issue_file, "r") as file:  # Read the file, get the local system's name.
                    content = file.readlines()
                    if len(content) > 0:  # Make sure this is not an empty file and return the information.
                        return content[0].strip().split()[0]

            # When search issue file is false, try tp get os-release file and find the information from that.
            if os.path.isfile(linux_release_file) and os.access(linux_release_file, os.R_OK):  # check the release file.
                with open(linux_release_file, "r") as file:  # Read the file, get the local system's name.
                    content = file.readlines()
                    for line in content:  # Because this file is a key-value pair file, we need to find the correct line and get the value from that.
                        if line.startswith("NAME="):
                            return line.strip().split("=")[1].strip('"')

            # All check false, return default value.
            return "Unknown"

    # build a global return, even though it may not be executed.
    return "Unknown"  # noqa


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineSystemVersion
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_local_machine_system_version() -> str:
    """
    This function returns the local machine system version.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: Unknown
    :return: str
    """
    try:
        return platform.version()

    # catch potential exception and return the error value.
    except (TypeError, ValueError, Exception):
        return "Unknown"


# TODO: CALL BY SPECIAL VALUE: GetLocalMachineSystemRelease
@lru_cache(maxsize=MAX_CACHE_VALUE)
def get_local_machine_system_release() -> str:
    """
    This function returns the local machine system release.
    It is used by configuration's default function list: packages.
    WARNING: When meet failure, it will return a special value: Unknown
    :return: str
    """
    try:
        return platform.release()

    # catch potential exception and return the error value.
    except (TypeError, ValueError, Exception):
        return "Unknown"

# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# IDENTIFICATION PRIVATE FUNCTION。
#
# region
# INTRODUCE SENTENCE.
# -> From here, is the private function which used to monitor the event and executive some function such as clear the netword.
# -> 
# -> 
#
# CODE SEGMENT START.

# This signal is used to monitor the network has been closed or not.
_MONITOR_SIGNAL: bool = False
_NETLINK_ROUTE = 0
_RTMGRP_LINK = 1
_RTM_NEWLINK = 16
_IFLA_IFNAME = 3
_IFF_RUNNING = 0x40  # 网卡物理连接标志

# Monitor the TCP heartbleed, call the function to flush the cache when network is changed or closed.
def _normal_monitor(timeout:  int = 4,
                    host:     str = "8.8.8.8",
                    port:     int = 53,
                    interval: int = 30) -> None:
    heartbleed: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    heartbleed.settimeout(timeout)

    # After create the socket, we can monitor the event without busy waiting.
    try:
        heartbleed.connect((host, port))

        # Build the connect success, start to monitor.
        while True:  # We can send the empty package to checkout.
            heartbleed.send(b"\x00")
            data = heartbleed.recv(1024)

            # Checkout the data, we can get the connection's information or not.
            if not data:
                raise ConnectionError

            # After that, we can take a sleep.
            time.sleep(interval)

    # Catch the error, change the cache.
    except (socket.error, ConnectionError):
        _on_network_change()

    # Finally, wer need to make sure that connection has been closed safety.
    finally:
        heartbleed.close()


def _parse_link_msg(data) -> tuple[Any, bool]:
    """解析netlink消息，提取接口名和运行状态"""
    # nlmsghdr (16字节) + ifinfomsg (16字节) 头部
    ifindex, ifi_flags = struct.unpack("i i", data[16:24])
    # 提取属性中的接口名
    offset = 32
    while offset < len(data):
        attr_len, attr_type = struct.unpack("h h", data[offset:offset + 4])
        if attr_type == _IFLA_IFNAME:
            name = data[offset + 4:offset + attr_len].decode('utf-8', 'ignore').strip('\x00')
            return name, bool(ifi_flags & _IFF_RUNNING)
        offset += (attr_len + 3) // 4 * 4
    return None, False


def _monitor_network(callback):
    sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, _NETLINK_ROUTE)
    sock.bind((os.getpid(), _RTMGRP_LINK))  # 仅监听网卡状态变化
    while True:
        data = sock.recv(4096)  # 此处阻塞，不消耗CPU
        # 跳过nlmsghdr头部
        offset = 0
        while offset < len(data):
            nl_len, nl_type = struct.unpack("i h", data[offset:offset + 6])
            if nl_type in (_RTM_NEWLINK, 16):
                name, is_running = _parse_link_msg(data[offset:offset + nl_len])
                if name:
                    callback(name, is_running)
            offset += nl_len


# Start executive, clear the cache and force to recalculate it.
def _on_network_change() -> None:
    get_system_ipv4.clear()
    get_system_ipv6.clear()
    get_system_mac.clear()
    get_system_mask.clear()
    get_system_gateway.clear()


def executive_monitor() -> None:
    if platform.system() == "Linux": threading.Thread(target=_monitor_network, daemon=True, args=(_on_network_change,)).start()
    else: threading.Thread(target=_normal_monitor, daemon=True).start()

# CODE SEGMENT END.
# endregion
#
# ----- SEPARATING LINE -----
#
# GLOBAL CODE SEGMENT END.
#
# endregion
#
# IDENTIFICATION END.
#
# ----- SOURCE END -----
