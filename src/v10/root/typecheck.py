import typing
import types


def _normalize_type(t):
    """将 None 字面量替换为 NoneType，统一类型表示。"""
    if t is None:
        # Python 3.10+ 有 types.NoneType，这里用 type(None) 兼容旧版
        return type(None)
    return t


def type_match(t1, t2) -> bool:
    """
    判断两个类型是否“宽松相等”。

    规则：
    - 如果任意一方为 typing.Any，返回 True。
    - 如果任意一方为 typing.Union，则检查另一方是否匹配 Union 中的某个成员。
    - 提取泛型的原始类型（origin），若原始类型相同则返回 True。
    - 若两个原始类型存在子类关系（is-subclass），也返回 True。
    - 支持 types.GenericAlias 动态泛型。
    """
    t1 = _normalize_type(t1)
    t2 = _normalize_type(t2)

    # Any 短路
    if t1 is typing.Any or t2 is typing.Any:
        return True

    # 处理 Union
    origin1 = typing.get_origin(t1)
    origin2 = typing.get_origin(t2)

    # 如果一方是 Union，展开并递归检查
    if origin1 is typing.Union:
        return any(type_match(arg, t2) for arg in typing.get_args(t1))
    if origin2 is typing.Union:
        return any(type_match(t1, arg) for arg in typing.get_args(t2))

    # 提取原始类型（泛型擦除参数）
    def _get_origin(t):
        o = typing.get_origin(t)
        if o is not None:
            return o
        elif isinstance(t, types.GenericAlias):  # 额外处理 types.GenericAlias （Python 3.9+ list[int] 等）
            return t.__origin__
        return None

    o1 = _get_origin(t1)
    o2 = _get_origin(t2)

    # 如果没提取到 origin，则使用类型本身
    if o1 is None:
        o1 = t1
    if o2 is None:
        o2 = t2

    # 原始类型相等
    if o1 == o2:
        return True

    # 子类关系检查
    if isinstance(o1, type) and isinstance(o2, type):
        try:
            if issubclass(o1, o2) or issubclass(o2, o1):  # noqa
                return True
        except TypeError:
            pass

    return False


def isinstance_loose(obj, type_hint) -> bool:
    """类似于 isinstance，但使用宽松的类型兼容规则，同时支持两种类型的直接比较。"""
    return type_match(type(obj) if not isinstance(obj, type) else obj, type_hint)
