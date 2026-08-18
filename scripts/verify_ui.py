"""在 mayapy standalone 下验证 UI 模块可导入。

注：Maya standalone 无法创建 Qt widget（会崩溃），widget 的完整验证
见 scripts/verify_maya_gui.py（需在真实 Maya GUI 内执行）。

运行：  "<Maya>/bin/mayapy.exe" scripts/verify_ui.py
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import maya.standalone  # noqa: E402

try:
    maya.standalone.initialize(name="python")
except Exception as e:  # pragma: no cover
    print("standalone initialize FAIL:", repr(e))
    sys.exit(0)

from dcc_checker.ui import common, dock_panel, main_menu, tool_item_widget  # noqa: E402

print("ui modules import ok")
print("ToolItemWidget:", tool_item_widget.ToolItemWidget.__name__)
print("ToolDockWidget:", dock_panel.ToolDockWidget.__name__)
print("menu install/uninstall callable:",
      callable(main_menu.install), callable(main_menu.uninstall))
print("maya_main_window (standalone -> None):", common.maya_main_window())
print("UI IMPORT VERIFY DONE")
