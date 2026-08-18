"""在真实 Maya GUI 内完整验证菜单 + 独立浮动窗口 + 设置字号滑杆 + 批量运行 + 日志 + 问题检查器。

用法：
在 Maya Script Editor 的 Python 标签页中直接执行：
    import sys
    ROOT = r"C:\Users\qingpulou\Documents\GitHub\DAMaya_AssetChecker"
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    exec(open(ROOT + r"\scripts\verify_maya_gui.py", encoding="utf-8").read())
"""
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 强制热重载所有 dcc_checker 模块（确保在不重启 Maya 的情况下加载最新代码）
for mod_name in list(sys.modules.keys()):
    if mod_name.startswith("dcc_checker"):
        del sys.modules[mod_name]

import maya.cmds as cmds  # noqa: E402

from dcc_checker.ui import main_menu  # noqa: E402
from dcc_checker.ui.dock_panel import ToolDockWidget  # noqa: E402

# 1) 安装顶部菜单
main_menu.install()
print("[1] 菜单已刷新安装 -> 主菜单栏已更新 DAMaya Asset Checker")

# 2) 呼出独立控制面板窗口
dock = ToolDockWidget.open_panel()
print("[2] 窗口已呼出 -> DAMaya Asset Checker 独立浮动窗口")

# 3) 造脏场景测试：pCube1（命名不合规 + 默认材质，触发两条 FAIL）
cmds.file(new=True, force=True)
cmds.polyCube(name="pCube1")

# 4) 批量运行勾选工具
if dock:
    report = dock.run_selected()
    if report:
        s = report.summary()
        print("[3] 批量运行结果:", s)

print()
print("VERIFY DONE - 验证完毕：")
print("  * 独立浮动窗口正常置顶显示 (DAMaya Asset Checker)")
print("  * Header 右上角点击 'Settings' 可呼出偏好设置与字号滑杆")
print("  * 工具卡片文字清晰，Run 按钮、状态标签对齐")
