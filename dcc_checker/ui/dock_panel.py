"""现代化 Dock 面板：左侧工具列表卡片 + 搜索过滤 + 统计仪表盘 + 右侧双标签控制台/问题检查器。"""
from __future__ import annotations

import os
import re
import time
from typing import List, Optional, Type

from dcc_checker.adapters.maya_adapter import MayaAdapter
from dcc_checker.core import BaseTool, RunReport, ToolContext, ToolRunner, render_log
from dcc_checker.core.registry import ToolRegistry
from dcc_checker.ui.common import QtCore, QtGui, QtWidgets, maya_main_window, shiboken
from dcc_checker.ui.group_container import CollapsibleGroup, group_tools_by_category
from dcc_checker.ui.styles import (
    COLOR_ERROR,
    COLOR_FAIL,
    build_dark_qss,
    font_scale_for_height,
)
from dcc_checker.ui.tool_item_widget import ToolItemWidget

WINDOW_TITLE = "DCC Asset Checker"
PANEL_OBJECT_NAME = "dccCheckerToolDock"
VERSION_STRING = "v1.0.0"


class ToolDockWidget(QtWidgets.QDockWidget):
    """寄宿在 Maya 主窗口的现代化检查器 Dock 面板。"""

    _instance = None

    @classmethod
    def open_panel(cls):
        """单例呼出面板：刷新工具列表、置前激活；面板被销毁时自动重建。"""
        inst = cls._instance
        is_valid = True
        if shiboken is not None and inst is not None:
            try:
                is_valid = shiboken.isValid(inst)
            except Exception:
                is_valid = False

        if inst is None or not is_valid:
            inst = cls()
            cls._instance = inst

        inst.refresh()
        QtWidgets.QDockWidget.show(inst)
        inst.raise_()
        inst.activateWindow()
        return inst

    def __init__(self, parent=None):
        if parent is None:
            parent = maya_main_window()
        super().__init__(WINDOW_TITLE, parent)
        self.setObjectName(PANEL_OBJECT_NAME)
        self.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        )

        self.registry = ToolRegistry()
        self.adapter = MayaAdapter()
        self._item_widgets: List[ToolItemWidget] = []
        self._last_report: Optional[RunReport] = None
        self._font_scale = 1.0
        self._resize_timer = None

        self._build_ui()
        self._apply_theme()

        if parent is not None:
            parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self)

    # ==================== 字体缩放 ====================

    def _apply_theme(self):
        """按当前基准字号应用主题（基准与面板高度/缩放相关）。"""
        base = round(13 * self._font_scale)
        base = max(11, min(17, base))
        self.setStyleSheet(build_dark_qss(base))

    def resizeEvent(self, event):
        """窗口缩放时按高度调整字体（带防抖，避免拖动时频繁重绘）。"""
        if QtCore is None:
            return
        super().resizeEvent(event)
        new_scale = font_scale_for_height(self.height())
        if abs(new_scale - self._font_scale) < 0.001:
            return
        self._font_scale = new_scale
        # debounce：闲置 120ms 后再应用主题
        if self._resize_timer is None and QtCore.QTimer is not None:
            self._resize_timer = QtCore.QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._apply_theme)
        if self._resize_timer is not None:
            self._resize_timer.start(120)

    # ==================== UI 构建 ====================

    def _build_ui(self):
        root = QtWidgets.QWidget()
        root.setObjectName("dcc_checker_root")
        main_layout = QtWidgets.QVBoxLayout(root)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # 1. 精简 Header（标题 + 版本）
        header = self._create_header_widget()
        main_layout.addWidget(header)

        # 2. 主体拆分视窗 (Splitter: 左工具卡片列表, 右日志/问题检查器)
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.setChildrenCollapsible(False)

        left_pane = self._create_left_tools_pane()
        right_pane = self._create_right_inspector_pane()

        splitter.addWidget(left_pane)
        splitter.addWidget(right_pane)
        splitter.setStretchFactor(0, 5)
        splitter.setStretchFactor(1, 6)
        main_layout.addWidget(splitter, 1)

        self.setWidget(root)

    def _create_header_widget(self) -> QtWidgets.QWidget:
        """构建顶部标题与版本徽章（不含操作按钮）。"""
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)

        # 标题
        title_label = QtWidgets.QLabel(WINDOW_TITLE)
        title_label.setStyleSheet("font-size: 1.17em; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_label)

        # 版本徽章
        ver_label = QtWidgets.QLabel(VERSION_STRING)
        ver_label.setStyleSheet("color: #808080; font-size: 0.83em; font-weight: bold; background: #252526; padding: 2px 6px; border-radius: 3px; border: 1px solid #333333;")
        layout.addWidget(ver_label)

        layout.addStretch()

        return widget

    def _create_left_tools_pane(self) -> QtWidgets.QWidget:
        """构建左侧工具区：搜索框（顶）→ 分组列表 → Refresh Tool List → Run Selected Checks（底）。"""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 搜索框（最上方）
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search tools by name, ID or category...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_filter_changed)
        layout.addWidget(self.search_input)

        # 计数标签
        self.tools_count_label = QtWidgets.QLabel("Available Tools")
        self.tools_count_label.setStyleSheet("color: #9a9a9a; font-size: 0.92em; font-weight: bold;")
        layout.addWidget(self.tools_count_label)

        # 滚动区域（折叠分组列表）
        self._list_host = QtWidgets.QWidget()
        self._list_layout = QtWidgets.QVBoxLayout(self._list_host)
        self._list_layout.setAlignment(QtCore.Qt.AlignTop if QtCore else None)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self._list_host)
        self.scroll_area.setMinimumWidth(280)
        layout.addWidget(self.scroll_area, 1)

        # 底部操作按钮（Refresh Tool List 在上，Run Selected Checks 在下）
        self.refresh_btn = QtWidgets.QPushButton("Refresh Tool List")
        self.refresh_btn.setObjectName("icon_button")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)

        self.run_btn = QtWidgets.QPushButton("Run Selected Checks")
        self.run_btn.setObjectName("primary_button")
        self.run_btn.setFixedHeight(34)
        self.run_btn.clicked.connect(self.run_selected)
        layout.addWidget(self.run_btn)

        return container

    def _create_right_inspector_pane(self) -> QtWidgets.QWidget:
        """构建右侧双标签页（Log 控制台与问题检查器）。"""
        self.tabs = QtWidgets.QTabWidget()

        # Tab 1: Log Console
        log_tab = QtWidgets.QWidget()
        log_layout = QtWidgets.QVBoxLayout(log_tab)
        log_layout.setContentsMargins(8, 8, 8, 8)
        log_layout.setSpacing(6)

        self.log_console = QtWidgets.QPlainTextEdit()
        self.log_console.setReadOnly(True)
        log_layout.addWidget(self.log_console, 1)

        # 兼容旧代码引用 self.log
        self.log = self.log_console

        log_btn_row = QtWidgets.QHBoxLayout()
        clear_btn = QtWidgets.QPushButton("Clear Console")
        clear_btn.clicked.connect(self.log_console.clear)

        export_btn = QtWidgets.QPushButton("Export Log")
        export_btn.clicked.connect(self.export_logs)

        copy_btn = QtWidgets.QPushButton("Copy All")
        copy_btn.clicked.connect(self._copy_logs_to_clipboard)

        log_btn_row.addWidget(clear_btn)
        log_btn_row.addWidget(export_btn)
        log_btn_row.addWidget(copy_btn)
        log_btn_row.addStretch()
        log_layout.addLayout(log_btn_row)

        # Tab 2: Issue Inspector (场景报错节点与一键选择)
        issues_tab = QtWidgets.QWidget()
        issues_layout = QtWidgets.QVBoxLayout(issues_tab)
        issues_layout.setContentsMargins(8, 8, 8, 8)
        issues_layout.setSpacing(6)

        self.issues_tree = QtWidgets.QTreeWidget()
        self.issues_tree.setHeaderLabels(["Tool / Issue Description", "Target Node"])
        self.issues_tree.setColumnWidth(0, 240)
        self.issues_tree.itemDoubleClicked.connect(self._on_issue_item_double_clicked)
        issues_layout.addWidget(self.issues_tree, 1)

        issues_btn_row = QtWidgets.QHBoxLayout()
        select_in_maya_btn = QtWidgets.QPushButton("Select in Maya")
        select_in_maya_btn.setToolTip("在 Maya 视口中高亮选中选中的报错物体")
        select_in_maya_btn.clicked.connect(self._select_current_issue_node)

        select_all_failed_btn = QtWidgets.QPushButton("Select All Failed")
        select_all_failed_btn.setToolTip("在 Maya 视口中高亮选中所有工具检出的异常模型")
        select_all_failed_btn.clicked.connect(self._select_all_failed_nodes)

        issues_btn_row.addWidget(select_in_maya_btn)
        issues_btn_row.addWidget(select_all_failed_btn)
        issues_btn_row.addStretch()
        issues_layout.addLayout(issues_btn_row)

        self.tabs.addTab(log_tab, "Log Console")
        self.tabs.addTab(issues_tab, "Issue Inspector")

        return self.tabs

    # ==================== 行为与逻辑 ====================

    def refresh(self) -> int:
        """重新扫描 tools/ 目录，按 category 重建折叠分组。"""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        self._item_widgets = []
        self._groups: List[CollapsibleGroup] = []

        tools = self.registry.refresh()
        grouped = group_tools_by_category(tools)
        for cat, classes in grouped.items():
            group = CollapsibleGroup(cat)
            group.set_count(len(classes))
            group.reorder_requested.connect(self._on_group_reorder)
            for tool_cls in classes:
                w = ToolItemWidget(tool_cls, run_callback=self.run_single_tool)
                group.add_card(w)
                self._item_widgets.append(w)
            self._list_layout.addWidget(group)
            self._groups.append(group)

        # 更新统计
        self._on_filter_changed()

        self._append_log(f"[INFO] Discovered and refreshed {len(self._item_widgets)} tools.")
        return len(self._item_widgets)

    def _on_group_reorder(self, dragged_id: str, drop_id: str):
        """根据折叠组发来的拖拽信息，把 dragged 卡片放到 drop 卡片之后（两者都同步）。"""
        def widget_by_id(tid: str) -> ToolItemWidget:
            return next(w for w in self._item_widgets if w.tool_cls.tool_id() == tid)

        # 在 _item_widgets 中做同样的「dragged 移到 drop 之后」操作
        di = self._item_widgets.index(widget_by_id(dragged_id))
        pi = self._item_widgets.index(widget_by_id(drop_id))
        if di == pi:
            return
        widget = self._item_widgets.pop(di)
        # 插入到 drop 之后：若 dragged 原在 drop 前，pop 后 drop 索引前移
        target = pi if di < pi else pi + 1
        self._item_widgets.insert(target, widget)

        # 同步对应折叠组内卡片物理顺序
        for group in self._groups:
            if getattr(group, "category", "") != getattr(widget.tool_cls, "category", ""):
                continue
            group.reorder_cards(dragged_id, drop_id)
            break

        self._append_log(f"[INFO] Tool order updated: {dragged_id} -> after {drop_id}")

    def select_all(self):
        for w in self._item_widgets:
            w.set_checked(True)

    def select_none(self):
        for w in self._item_widgets:
            w.set_checked(False)

    def invert_selection(self):
        for w in self._item_widgets:
            w.set_checked(not w.is_checked())

    def _on_filter_changed(self):
        """响应搜索框变化，实时过滤显示项（分类导航交给折叠组）。"""
        search_text = self.search_input.text().strip()

        visible_count = 0
        for w in self._item_widgets:
            matches = w.matches_filter(search_text, "")
            w.setVisible(matches)
            if matches:
                visible_count += 1

        total = len(self._item_widgets)
        if search_text:
            self.tools_count_label.setText(f"Tools ({visible_count} matched / {total} total)")
        else:
            self.tools_count_label.setText(f"Tools ({total} total)")

    def run_selected(self) -> Optional[RunReport]:
        """批量运行所有勾选工具。"""
        selected_widgets = [w for w in self._item_widgets if w.is_checked()]
        selected_classes = [w.tool_cls for w in selected_widgets]

        if not selected_classes:
            self._append_log("[WARN] No tools selected to run.")
            return None

        return self._execute_tools(selected_classes, selected_widgets)

    def run_single_tool(self, tool_cls: Type[BaseTool]) -> RunReport:
        """独立运行单条工具。"""
        matching_widgets = [w for w in self._item_widgets if w.tool_cls.tool_id() == tool_cls.tool_id()]
        return self._execute_tools([tool_cls], matching_widgets)

    def _execute_tools(self, tool_classes: List[Type[BaseTool]], target_widgets: List[ToolItemWidget]) -> RunReport:
        """核心执行流水线：更新进度、渲染彩色日志与填装问题检查器。"""
        ctx = ToolContext(adapter=self.adapter)
        runner = ToolRunner(ctx=ctx)

        # 重置对应组件状态
        for w in target_widgets:
            w.set_running()

        self.issues_tree.clear()
        total_count = len(tool_classes)
        self._append_log(f"=== Starting execution: {total_count} tool(s) ===")

        report = runner.run(tool_classes, ctx=ctx)
        self._last_report = report

        # 更新卡片与渲染日志
        for record in report.records:
            for line in render_log(record.tool_name, record.result):
                self._append_log(line)
            self._update_item(record)
            self._populate_issues_for_record(record)

        # 汇总统计
        s = report.summary()
        self._append_log(
            f"=== Execution Completed: {s['pass']} Passed / {s['fail']} Failed / {s['error']} Errored ==="
        )

        # 如果有失败项，自动切换到问题检查器 Tab
        if s.get("fail", 0) > 0 or s.get("error", 0) > 0:
            self.tabs.setCurrentIndex(1)

        return report

    def _update_item(self, record):
        for w in self._item_widgets:
            if w.tool_cls.tool_id() == record.tool_id:
                w.set_result(record.result)

    def _append_log(self, text: str):
        """附带精确时间戳的日志输出。"""
        t = time.strftime("[%H:%M:%S]")
        self.log_console.appendPlainText(f"{t} {text}")

    # ==================== 问题检查器与视口交互 ====================

    def _populate_issues_for_record(self, record):
        """将失败或异常记录解析并挂入 Issue Inspector 树形列表。"""
        if record.result.ok:
            return

        tool_item = QtWidgets.QTreeWidgetItem(self.issues_tree)
        status_tag = "[FAIL]" if not record.result.is_error else "[ERROR]"
        tool_item.setText(0, f"{status_tag} {record.tool_name}")
        tool_item.setText(1, record.tool_id)

        # 设置状态颜色
        color = QtGui.QColor(COLOR_FAIL if not record.result.is_error else COLOR_ERROR)
        tool_item.setForeground(0, QtGui.QBrush(color))
        tool_item.setExpanded(True)

        for msg in record.result.messages:
            msg_str = str(msg).strip()
            # 提取可能关联的 Maya 节点名称 (如 'pCube1', 'SM_Box', 'lambert1')
            node_name = self._extract_node_name(msg_str)
            child = QtWidgets.QTreeWidgetItem(tool_item)
            child.setText(0, msg_str)
            if node_name:
                child.setText(1, node_name)
                child.setToolTip(1, f"Double-click to select '{node_name}' in Maya")
            else:
                child.setText(1, "-")

    def _extract_node_name(self, msg: str) -> Optional[str]:
        """从错误消息中尝试提取节点名。"""
        parts = re.findall(r"[:\s]([a-zA-Z0-9_|]+)", msg)
        for part in parts:
            if part and not part.lower() in ("pass", "fail", "error", "missing", "uses", "none", "true", "false"):
                return part
        return None

    def _on_issue_item_double_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int):
        """双击问题节点条目时，在 Maya 中选中物体。"""
        node_name = item.text(1)
        if node_name and node_name != "-":
            self._select_node_in_maya(node_name)

    def _select_current_issue_node(self):
        """选中当前在树中选中的节点。"""
        item = self.issues_tree.currentItem()
        if not item:
            return
        node_name = item.text(1)
        if node_name and node_name != "-":
            self._select_node_in_maya(node_name)

    def _select_all_failed_nodes(self):
        """选中所有检出异常的节点。"""
        nodes = []
        root = self.issues_tree.invisibleRootItem()
        for i in range(root.childCount()):
            tool_item = root.child(i)
            for j in range(tool_item.childCount()):
                sub = tool_item.child(j)
                n = sub.text(1)
                if n and n != "-" and n not in nodes:
                    nodes.append(n)

        if nodes:
            self._select_node_in_maya(nodes)
        else:
            self._append_log("[INFO] No specific Maya nodes to select.")

    def _select_node_in_maya(self, target):
        """调用 Maya API 在视口中选中目标节点。"""
        try:
            import maya.cmds as cmds
            if isinstance(target, str):
                target = [target]

            existing = [n for n in target if cmds.objExists(n)]
            if existing:
                cmds.select(existing, replace=True)
                self._append_log(f"[INFO] Selected {len(existing)} object(s) in Maya: {existing}")
            else:
                self._append_log(f"[WARN] Objects do not exist in scene: {target}")
        except Exception as e:
            self._append_log(f"[WARN] Viewport selection unavailable: {e}")

    def _copy_logs_to_clipboard(self):
        """复制日志到系统剪贴板。"""
        clipboard = QtWidgets.QApplication.clipboard()
        if clipboard:
            clipboard.setText(self.log_console.toPlainText())
            self._append_log("[INFO] Log console text copied to clipboard.")

    def export_logs(self):
        """导出当前日志到本地文件。"""
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        log_file = os.path.join(desktop, f"dcc_checker_log_{int(time.time())}.txt")
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(self.log_console.toPlainText())
            self._append_log(f"[SUCCESS] Logs exported to: {log_file}")
            QtWidgets.QMessageBox.information(
                self,
                "Export Successful",
                f"Logs exported to:\n{log_file}"
            )
        except Exception as e:
            self._append_log(f"[ERROR] Failed to export logs: {e}")
