"""在 Maya 主菜单栏添加「DAMaya Asset Checker」下拉菜单。

参考 DAMaya_MCP 的挂载方式：
* 用全局 MEL 变量 ``$gMainWindow`` 获取主窗口菜单栏（不硬编码 "MayaWindow"）
* ``cmds.about(batch=True)`` 批量模式保护
* 幂等安装（先删旧菜单再建）
* 提供控制面板呼出、一键全量检查、问题节点高亮与偏好设置等菜单项
"""
from __future__ import annotations

import maya.cmds as cmds
import maya.mel as mel

MENU_NAME = "dccCheckerMenu"
MENU_LABEL = "DAMaya Asset Checker"


def _main_window_menu_bar():
    """返回 Maya 主窗口菜单栏名，失败回退到 "MayaWindow"。"""
    try:
        g_main_window = mel.eval("$tmp = $gMainWindow;")
    except Exception:
        g_main_window = None
    return g_main_window or "MayaWindow"


def show_dock_panel():
    """呼出控制面板独立窗口。"""
    from dcc_checker.ui.dock_panel import ToolDockWidget

    return ToolDockWidget.open_panel()


def _open_settings():
    """打开设置窗口。"""
    dock = show_dock_panel()
    if dock:
        dock.open_settings()


def _run_all_checks():
    """在面板中一键执行所有「检测类」工具检查（动作类不执行，避免破坏性操作）。"""
    dock = show_dock_panel()
    if dock:
        dock.select_checkers_only()
        dock.run_selected()


def _select_all_failed():
    """在 Maya 视口中高亮选中所有检出的问题模型。"""
    dock = show_dock_panel()
    if dock:
        dock._select_all_failed_nodes()


def _show_help():
    """打开帮助文档或项目说明。"""
    import webbrowser
    webbrowser.open("https://github.com/NightXDreamin/DAMaya_AssetChecker")


def install():
    """安装菜单（幂等）。批量模式（batch）下跳过。"""
    if cmds.about(batch=True):
        return
    if cmds.menu(MENU_NAME, q=True, exists=True):
        cmds.deleteUI(MENU_NAME)

    main_menu = cmds.menu(MENU_NAME, label=MENU_LABEL, parent=_main_window_menu_bar(), tearOff=True)

    # 1. 呼出主面板
    cmds.menuItem(
        label="Open Control Panel (打开控制面板)",
        command=lambda *args: show_dock_panel(),
    )
    cmds.menuItem(
        label="Settings (偏好设置)",
        command=lambda *args: _open_settings(),
    )
    cmds.menuItem(divider=True)

    # 2. 快捷运行与选择子菜单
    cmds.menuItem(
        label="Run All Checks (一键全量检查)",
        command=lambda *args: _run_all_checks(),
    )
    cmds.menuItem(
        label="Select Failed Objects (全选问题物体)",
        command=lambda *args: _select_all_failed(),
    )
    cmds.menuItem(divider=True)

    # 3. 帮助
    cmds.menuItem(
        label="Help & Documentation (帮助文档)",
        command=lambda *args: _show_help(),
    )


def uninstall():
    """卸载菜单。"""
    if cmds.menu(MENU_NAME, q=True, exists=True):
        cmds.deleteUI(MENU_NAME)
