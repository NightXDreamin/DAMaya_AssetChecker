"""UI 公共辅助：获取 Maya 主窗口与 Qt 兼容导入。"""
from __future__ import annotations

# Qt 兼容导入（支持 PySide6 与 PySide2）
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    QtMimeData = QtCore.QMimeData
    QtByteArray = QtCore.QByteArray
    QtPoint = QtCore.QPoint
    QtDrag = QtGui.QDrag
    try:
        import shiboken6 as shiboken
    except ImportError:
        shiboken = None
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
        QtMimeData = QtCore.QMimeData
        QtByteArray = QtCore.QByteArray
        QtPoint = QtCore.QPoint
        QtDrag = QtGui.QDrag
        try:
            import shiboken2 as shiboken
        except ImportError:
            shiboken = None
    except ImportError:
        QtWidgets = None
        QtCore = None
        QtGui = None
        shiboken = None
        QtMimeData = None
        QtByteArray = None
        QtPoint = None
        QtDrag = None


def is_qt_available() -> bool:
    """检查 Qt 绑定库是否可用。"""
    return QtWidgets is not None


def maya_main_window():
    """返回 Maya 主窗口 QMainWindow；非 GUI 环境（standalone）返回 None。"""
    if not is_qt_available() or shiboken is None:
        return None
    try:
        import maya.OpenMayaUI as omui

        ptr = omui.MQtUtil.mainWindow()
        if ptr:
            return shiboken.wrapInstance(int(ptr), QtWidgets.QMainWindow)
    except Exception:
        pass
    return None
