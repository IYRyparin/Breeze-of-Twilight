#!/usr/bin/env python3
# tool.py - 轻量级变量追踪器（无深拷贝，过滤外部库）
import sys
import os
import runpy
from collections import defaultdict

# ========== 配置 ==========
# 获取当前工作目录的绝对路径，仅追踪该目录下的源码
TARGET_DIR = os.path.abspath(os.getcwd())
# 输出值的最大显示长度
MAX_VAL_LEN = 80

# 存储每个栈帧上一次变量的 repr 快照
previous_reprs = defaultdict(dict)


def safe_repr(obj, max_len=MAX_VAL_LEN):
    """安全地获取对象的 repr，避免因循环引用或异常导致崩溃"""
    try:
        s = repr(obj)
        return s[:max_len] + ("..." if len(s) > max_len else "")
    except Exception:
        return "<无法获取 repr>"


def trace_variables(frame, event, arg):
    if event != 'line':
        return trace_variables

    # ========== 核心过滤：只追踪当前目录下的业务代码 ==========
    filename = frame.f_code.co_filename
    if not filename:
        return trace_variables

    abs_filename = os.path.abspath(filename)
    # 排除 Python 内置虚拟文件名（如 <string>、<frozen>）以及外部库
    if not abs_filename.startswith(TARGET_DIR):
        return trace_variables

    frame_id = id(frame)

    # 过滤掉 Python 内部隐式变量（如 __name__, __loader__ 等），只保留业务变量
    # 注意：这里使用 frame.f_locals，包含了局部和全局（模块级）变量
    current_vars = {k: v for k, v in frame.f_locals.items()
                    if not k.startswith('__') and k not in ('builtins', '__builtins__')}

    # 获取当前帧的 repr 快照
    current_reprs = {k: safe_repr(v) for k, v in current_vars.items()}
    prev_reprs = previous_reprs[frame_id]

    # 1. 计算差异
    created = set(current_reprs.keys()) - set(prev_reprs.keys())
    deleted = set(prev_reprs.keys()) - set(current_reprs.keys())

    # 2. 检查修改（比较 repr 字符串是否变化，既能捕捉内部变动，又无需深拷贝）
    modified = {}
    common_keys = set(current_reprs.keys()) & set(prev_reprs.keys())
    for key in common_keys:
        if current_reprs[key] != prev_reprs[key]:
            modified[key] = (prev_reprs[key], current_reprs[key])

    # 3. 如果有任何变动，打印详细信息
    if created or deleted or modified:
        # 获取代码位置（显示相对路径，更清爽）
        try:
            rel_path = os.path.relpath(abs_filename, TARGET_DIR)
        except ValueError:
            rel_path = abs_filename
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name or '<模块>'

        print(f"\n🔍 [{rel_path}:{lineno}] 在函数 {func_name} 中:")

        if created:
            print(f"  ✅ 创建变量: {', '.join(created)}")
            for k in created:
                print(f"      {k} = {current_reprs[k]}")

        if modified:
            print(f"  🔄 修改变量:")
            for k, (old, new) in modified.items():
                print(f"      {k} : {old}  ➜  {new}")

        if deleted:
            print(f"  ❌ 删除变量: {', '.join(deleted)}")
            for k in deleted:
                print(f"      {k} (原值: {prev_reprs[k]})")

        # 额外输出此时所有变量的完整快照
        if current_reprs:
            print(f"  📦 当前全部变量快照:")
            for k, v in current_reprs.items():
                print(f"      {k} = {v}")

    # 更新快照（只保存 repr 字符串，避免存储对象本身）
    previous_reprs[frame_id] = current_reprs
    return trace_variables


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python tool.py target.py")
        sys.exit(1)

    target_script = sys.argv[1]

    # 如果 target.py 在当前目录，将其加入追踪
    print(f"📌 追踪目录: {TARGET_DIR}")
    print(f"📄 运行脚本: {target_script}\n" + "-" * 40)

    sys.settrace(trace_variables)

    try:
        # 以 __main__ 方式运行目标脚本
        runpy.run_path(target_script, run_name="__main__")
    except Exception as e:
        print(f"\n⚠️ 目标脚本执行异常: {e}")
    finally:
        sys.settrace(None)
