"""在真实 Maya GUI 内完整验证菜单 + dock + 批量运行 + 绿红 + 日志 + 问题检查器。

用法（任选其一）：
1. 在 Maya Script Editor 的 Python 标签页执行：
       exec(open(r"<repo>/scripts/verify_maya_gui.py").read())
2. 或用 mayapy 之外的真实 Maya：把本文件内容粘贴到 Script Editor 运行。
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import maya.cmds as cmds  # noqa: E402

from dcc_checker.ui import main_menu  # noqa: E402

# 1) 安装顶部菜单
main_menu.install()
print("[1] 菜单已安装 -> 主菜单栏应出现 DCC Checker -> Open Tool Dock")

# 2) 造脏场景：pCube1（命名不合规 + 默认材质，触发两条 FAIL）
cmds.file(new=True, force=True)
cmds.polyCube(name="pCube1")

# 3) 呼出 dock 面板
from dcc_checker.ui.dock_panel import ToolDockWidget  # noqa: E402

dock = ToolDockWidget.open_panel()
print("[2] dock 已呼出 -> 应看到现代化深色面板（搜索栏、按类别折叠分组、右侧 Log Console / Issue Inspector）")

# 4) 批量运行勾选工具
report = dock.run_selected()
s = report.summary()
print("[3] 批量运行结果:", s)
print("    (pCube1 触发 naming.prefix 与 material.default 两条 FAIL -> 红点/FAIL 徽标)")

print()
print("VERIFY DONE - 请目视确认：")
print("  * 顶部菜单出现且可呼出面板 (DCC Checker)")
print("  * 工具按 category 折叠分组，组标题可展开/折叠")
print("  * 工具卡片带 Checkbox、[CHECKER]/[ACTION] 徽标、Run 独立测试按钮")
print("  * 搜索框支持按名称/ID/描述/类别实时过滤")
print("  * 右侧 Log Console 有精准时间戳与日志")
print("  * 右侧 Issue Inspector 树状列出 pCube1，双击可在 Maya 视口中高亮选中模型")
