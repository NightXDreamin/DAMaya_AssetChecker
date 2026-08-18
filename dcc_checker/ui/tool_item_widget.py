"""单条工具卡片行组件：复选框 + 名称 + 类型徽标 + 状态指示 + 单工具执行。"""
from __future__ import annotations

from typing import Callable, Optional

from dcc_checker.core import ToolResult, ToolStatus, status_color
from dcc_checker.ui.common import (
    QtByteArray,
    QtCore,
    QtDrag,
    QtGui,
    QtMimeData,
    QtWidgets,
)
from dcc_checker.ui.styles import (
    BG_CARD,
    BG_CARD_HOVER,
    BORDER_DARK,
    BORDER_LIGHT,
    COLOR_ERROR,
    COLOR_FAIL,
    COLOR_IDLE,
    COLOR_PASS,
    COLOR_RUNNING,
    category_badge_style,
    status_badge_style,
)


class ToolItemWidget(QtWidgets.QFrame):
    """面板工具列表中的一行卡片组件。"""

    def __init__(self, tool_cls, parent=None, run_callback: Optional[Callable] = None, base_font_size: int = 13):
        super().__init__(parent)
        self.tool_cls = tool_cls
        self.run_callback = run_callback
        self._current_result = None
        self._font_size = base_font_size
        self._current_color = COLOR_IDLE

        self.setObjectName("tool_card")
        self.setStyleSheet(f"""
            QFrame#tool_card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
            }}
            QFrame#tool_card:hover {{
                border-color: {BORDER_LIGHT};
                background-color: {BG_CARD_HOVER};
            }}
        """)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)

        # 1. 勾选框 —— 只有检测类工具默认勾选，动作类默认不勾（避免误执行破坏性操作）
        is_checker = getattr(tool_cls, "is_checker", True)
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(is_checker)
        layout.addWidget(self.checkbox)

        # 2. 工具主信息（标题与描述）
        info_layout = QtWidgets.QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setContentsMargins(0, 0, 0, 0)

        title_row = QtWidgets.QHBoxLayout()
        title_row.setSpacing(8)
        title_row.setContentsMargins(0, 0, 0, 0)

        # 工具显示名
        self.name_label = QtWidgets.QLabel(tool_cls.name or tool_cls.tool_id())
        self.name_label.setStyleSheet(f"font-weight: bold; color: #ffffff; font-size: {self._font_size}px;")
        title_row.addWidget(self.name_label)

        # 类型徽标 (CHECKER / ACTION)
        self.type_badge = QtWidgets.QLabel("CHECKER" if is_checker else "ACTION")
        self.type_badge.setStyleSheet(category_badge_style(is_checker, self._font_size))
        title_row.addWidget(self.type_badge)

        # 类别小标签
        cat_name = getattr(tool_cls, "category", "General")
        self.cat_label = QtWidgets.QLabel(f"[{cat_name}]")
        self.cat_label.setStyleSheet(f"color: #888888; font-size: {max(9, self._font_size - 2)}px;")
        title_row.addWidget(self.cat_label)
        title_row.addStretch()

        info_layout.addLayout(title_row)

        # 描述文本（如有）
        desc = getattr(tool_cls, "description", "")
        if desc:
            self.desc_label = QtWidgets.QLabel(desc)
            self.desc_label.setStyleSheet(f"color: #9e9e9e; font-size: {max(10, self._font_size - 1)}px;")
            self.desc_label.setWordWrap(True)
            info_layout.addWidget(self.desc_label)
        else:
            self.desc_label = None

        layout.addLayout(info_layout, 1)

        # 3. 单工具测试运行按钮 (Run)
        self.run_btn = QtWidgets.QPushButton("Run")
        self.run_btn.setObjectName("icon_button")
        self.run_btn.setToolTip("单独运行此工具")
        self.run_btn.setMinimumWidth(54)
        self.run_btn.setMinimumHeight(24)
        self.run_btn.clicked.connect(self._on_run_clicked)
        layout.addWidget(self.run_btn)

        # 4. 状态指示徽标
        self.status_label = QtWidgets.QLabel("[IDLE]")
        self.status_label.setFixedWidth(72)
        if QtCore is not None:
            self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self._set_status_display(COLOR_IDLE, "[IDLE]")
        layout.addWidget(self.status_label)

        # 兼容旧代码引用 status_dot
        self.status_dot = self.status_label

        # 提示信息
        tooltip_text = f"ID: {tool_cls.tool_id()}\nCategory: {cat_name}\nType: {'Checker' if is_checker else 'Action'}"
        if desc:
            tooltip_text += f"\nDescription: {desc}"
        self.setToolTip(tooltip_text)

        # 拖拽排序状态
        self._drag_start_pos = None

    # ---- 动态字号调整 ----
    def update_font_size(self, base_px: int):
        """动态更新组件字号。"""
        self._font_size = base_px
        is_checker = getattr(self.tool_cls, "is_checker", True)
        self.name_label.setStyleSheet(f"font-weight: bold; color: #ffffff; font-size: {base_px}px;")
        if self.desc_label:
            self.desc_label.setStyleSheet(f"color: #9e9e9e; font-size: {max(10, base_px - 1)}px;")
        self.cat_label.setStyleSheet(f"color: #888888; font-size: {max(9, base_px - 2)}px;")
        self.type_badge.setStyleSheet(category_badge_style(is_checker, base_px))
        self.status_label.setStyleSheet(status_badge_style(self._current_color, base_px))

    # ---- 拖拽启动 ----
    TOOL_DRAG_MIME = "application/x-dcc-checker-tool"

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (
            self._drag_start_pos is not None
            and (event.pos() - self._drag_start_pos).manhattanLength()
            >= QtWidgets.QApplication.startDragDistance()
        ):
            self._start_drag()
            self._drag_start_pos = None
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_start_pos = None
        super().mouseReleaseEvent(event)

    def _start_drag(self):
        if QtDrag is None:
            return
        mime = QtMimeData()
        mime.setData(self.TOOL_DRAG_MIME, QtByteArray(self.tool_cls.tool_id().encode("utf-8")))
        drag = QtDrag(self)
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.MoveAction | QtCore.Qt.CopyAction)

    # ---- 交互与事件 ----
    def _on_run_clicked(self):
        """点击单个运行按钮。"""
        if self.run_callback:
            self.run_callback(self.tool_cls)

    def _set_status_display(self, color: str, text: str):
        """更新状态文本与高亮样式。"""
        self._current_color = color
        self.status_label.setText(text)
        self.status_label.setStyleSheet(status_badge_style(color, self._font_size))

    # ---- 对外状态与控制接口（兼容现有测试和调用） ----
    def is_checked(self) -> bool:
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool) -> None:
        self.checkbox.setChecked(checked)

    def set_status(self, color: str, text: Optional[str] = None) -> None:
        """按颜色设置状态。"""
        if text is None:
            text = "[READY]"
        self._set_status_display(color, text)

    def set_running(self) -> None:
        """设置为运行中状态。"""
        self._set_status_display(COLOR_RUNNING, "[RUNNING]")

    def set_result(self, result: ToolResult) -> None:
        """按 ToolResult 设置结果状态（只显示纯状态名，不拼接数字，保持对齐）。"""
        self._current_result = result
        if result.status is ToolStatus.PASS:
            self._set_status_display(COLOR_PASS, "[PASS]")
        elif result.status is ToolStatus.FAIL:
            self._set_status_display(COLOR_FAIL, "[FAIL]")
        elif result.status is ToolStatus.ERROR:
            self._set_status_display(COLOR_ERROR, "[ERROR]")
        else:
            self._set_status_display(COLOR_IDLE, "[IDLE]")

    def reset_status(self) -> None:
        """重置为初始 IDLE 状态。"""
        self._current_result = None
        self._set_status_display(COLOR_IDLE, "[IDLE]")

    def matches_filter(self, search_text: str, category_filter: str) -> bool:
        """检查本工具是否符合搜索词与分类筛选。"""
        cat = getattr(self.tool_cls, "category", "General")
        if category_filter and category_filter != "All" and cat != category_filter:
            return False

        if not search_text:
            return True

        search_lower = search_text.lower()
        tool_id = self.tool_cls.tool_id().lower()
        tool_name = (self.tool_cls.name or "").lower()
        tool_desc = (getattr(self.tool_cls, "description", "") or "").lower()

        return (
            search_lower in tool_id
            or search_lower in tool_name
            or search_lower in tool_desc
            or search_lower in cat.lower()
        )
