"""按 category 的折叠分组容器，及组内拖拽排序。

* ``group_tools_by_category`` —— 把工具类列表按 category 分组（纯函数，可单测）
* ``CollapsibleGroup`` —— 一个 QFrame 折叠组：标题行（组名 + 数量 + ▼/▶）+ 可拖拽排序的卡片容器
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Type

from dcc_checker.core import BaseTool
from dcc_checker.ui.common import QtCore, QtGui, QtWidgets
from dcc_checker.ui.styles import (
    BG_CARD,
    BORDER_DARK,
    BORDER_LIGHT,
    group_title_style,
)


def group_tools_by_category(
    tool_classes: Sequence[Type[BaseTool]],
) -> Dict[str, List[Type[BaseTool]]]:
    """把工具类列表按 category 归组，保持工具原顺序，返回有序字典。"""
    groups: Dict[str, List[Type[BaseTool]]] = {}
    for cls in tool_classes:
        cat = str(getattr(cls, "category", "General") or "General")
        groups.setdefault(cat, []).append(cls)
    return groups


def sort_cards_by_y(card_y: Dict[str, int]) -> List[str]:
    """按每个卡片的顶部 y 坐标升序返回 tool_id 列表（拖拽重排依据）。"""
    return sorted(card_y, key=lambda tid: card_y[tid])


if QtWidgets is None:
    # 无 Qt 环境（系统 Python 跑纯函数单测）：CollapsibleGroup 不可用
    CollapsibleGroup = None  # type: ignore[assignment, misc]
else:

    class CollapsibleGroup(QtWidgets.QFrame):
        """一个可折叠、组内可拖拽排序的工具分类组。"""

        TOOL_DRAG_MIME = "application/x-dcc-checker-tool"
        # 发射参数：(dragged_id, drop_id)
        reorder_requested = QtCore.Signal(str, str)

        def __init__(self, category: str, parent=None):
            super().__init__(parent)
            self.category = category
            self._expanded = True
            self._cards: List[QtWidgets.QWidget] = []

            self.setObjectName("group_frame")
            self.setStyleSheet(
                f"QFrame#group_frame {{ background: {BG_CARD}; border: 1px solid {BORDER_DARK}; border-radius: 4px; }}"
            )

            outer = QtWidgets.QVBoxLayout(self)
            outer.setContentsMargins(0, 0, 0, 0)
            outer.setSpacing(0)

            # 标题行（点击折叠/展开）
            self._build_header()

            # 卡片容器（接受拖拽）
            self.cards_host = QtWidgets.QWidget()
            self.cards_host.setAcceptDrops(True)
            self.cards_layout = QtWidgets.QVBoxLayout(self.cards_host)
            self.cards_layout.setContentsMargins(4, 4, 4, 4)
            self.cards_layout.setSpacing(4)
            self.cards_layout.setAlignment(QtCore.Qt.AlignTop)

            self.cards_host.installEventFilter(self)
            outer.addWidget(self.cards_host)

        # ---- 标题 ----
        def _build_header(self):
            self.header_btn = QtWidgets.QToolButton()
            self.header_btn.setObjectName("group_title")
            self.header_btn.setStyleSheet(group_title_style())
            self.header_btn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.header_btn.setIcon(self._arrow_icon(expanded=True))
            self.header_btn.setCheckable(True)
            self.header_btn.setChecked(True)
            self.header_btn.clicked.connect(self.toggle)
            self.header_btn.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
            )

            outer = self.layout()
            outer.addWidget(self.header_btn)
            self.arrow_icon = self.header_btn.icon()  # 复用

        def _arrow_icon(self, expanded: bool) -> QtGui.QIcon:
            # 用 QToolButton 自带箭头（向下=展开 / 向右=折叠）
            style = QtWidgets.QStyle.StandardPixmap(
                QtWidgets.QStyle.SP_ArrowDown if expanded else QtWidgets.QStyle.SP_ArrowRight
            )
            return self.style().standardIcon(style)

        def toggle(self, checked: Optional[bool] = None):
            """展开/折叠。"""
            if checked is None:
                checked = not self._expanded
            self._expanded = bool(checked)
            self.header_btn.setChecked(self._expanded)
            self.header_btn.setIcon(self._arrow_icon(self._expanded))
            self.cards_host.setVisible(self._expanded)

        def set_expanded(self, expanded: bool):
            if expanded != self._expanded:
                self.toggle(expanded)

        def is_expanded(self) -> bool:
            return self._expanded

        # ---- 卡片管理 ----
        def add_card(self, widget: QtWidgets.QWidget):
            self.cards_layout.addWidget(widget)
            self._cards.append(widget)

        def clear_cards(self):
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.deleteLater()
            self._cards = []

        def reorder_cards(self, moved_id: str, anchor_id: str):
            """把 moved_id 对应的卡片放到 anchor_id 卡片之后（组内重排）。"""
            ids = [getattr(c, "tool_cls").tool_id() for c in self._cards]
            if moved_id not in ids or anchor_id not in ids:
                return
            mi = ids.index(moved_id)
            ai = ids.index(anchor_id)
            if mi == ai:
                return
            moved = self._cards.pop(mi)
            # 插入到 anchor 之后：若 moved 原在 anchor 前，pop 后 ai 前移
            target = ai if mi < ai else ai + 1
            self._cards.insert(target, moved)
            self._rebuild_layout()

        def _rebuild_layout(self):
            # 清空布局项（不释放对象），按 _cards 顺序重插
            while self.cards_layout.count():
                item = self.cards_layout.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
            for card in self._cards:
                self.cards_layout.addWidget(card)

        def set_count(self, count: int):
            self.header_btn.setText(f"  {self.category}   ({count})")

        # ---- 拖拽排序 ----
        def eventFilter(self, obj, event):
            if obj is self.cards_host:
                if event.type() == QtCore.QEvent.DragEnter:
                    return self._on_drag_enter(event)
                if event.type() == QtCore.QEvent.DragMove:
                    return self._on_drag_move(event)
                if event.type() == QtCore.QEvent.Drop:
                    return self._on_drop(event)
            return super().eventFilter(obj, event)

        def _drag_mime_data(self, event) -> Optional[QtCore.QMimeData]:
            mime = event.mimeData()
            if mime and mime.hasFormat(self.TOOL_DRAG_MIME):
                return mime
            return None

        def _on_drag_enter(self, event) -> bool:
            if self._drag_mime_data(event):
                event.acceptProposedAction()
                return True
            event.ignore()
            return False

        def _on_drag_move(self, event) -> bool:
            if self._drag_mime_data(event):
                event.acceptProposedAction()
                return True
            event.ignore()
            return False

        def _on_drop(self, event) -> bool:
            mime = self._drag_mime_data(event)
            if not mime:
                event.ignore()
                return False

            dragged_id = str(mime.data(self.TOOL_DRAG_MIME).data().decode("utf-8", "replace"))
            drop_id = self._tool_id_at_y(event.pos().y())

            ids = [getattr(c, "tool_cls").tool_id() for c in self._cards]
            if dragged_id in ids and drop_id in ids:
                self.reorder_requested.emit(dragged_id, drop_id)
                event.acceptProposedAction()
                return True
            event.ignore()
            return False

        def _card_id_at_y(self, y: int) -> Optional[str]:
            for card in self._cards:
                if card.isVisible():
                    top = card.mapTo(self.cards_host, QtCore.QPoint(0, 0)).y()
                    bottom = top + card.height()
                    if top <= y < bottom:
                        return getattr(card, "tool_cls").tool_id()
            return None

        def _tool_id_at_y(self, y: int) -> str:
            tid = self._card_id_at_y(y)
            if tid is not None:
                return tid
            return self._cards[-1].tool_cls.tool_id() if self._cards else ""
