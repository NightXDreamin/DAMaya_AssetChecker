"""UI 样式与主题定义模块。

提供深色工业风 QSS 样式表、状态颜色映射及视觉组件辅助。
支持动态字号缩放，完美适配不同屏幕 DPI 与用户自定义偏好。
"""
from __future__ import annotations

# 颜色常量定义
BG_MAIN = "#1e1e1e"
BG_PANEL = "#252526"
BG_CARD = "#2d2d2d"
BG_CARD_HOVER = "#333333"
BG_INPUT = "#1a1a1a"
BG_SELECTED = "#094771"

BORDER_DARK = "#333333"
BORDER_MID = "#3e3e42"
BORDER_LIGHT = "#4f4f54"

TEXT_BRIGHT = "#ffffff"
TEXT_NORMAL = "#d4d4d4"
TEXT_MUTED = "#9a9a9a"
TEXT_DIM = "#707070"

ACCENT_BLUE = "#0e639c"
ACCENT_BLUE_HOVER = "#1177bb"
ACCENT_BLUE_PRESSED = "#0d5c90"

COLOR_PASS = "#2ecc71"
COLOR_FAIL = "#e74c3c"
COLOR_ERROR = "#c0392b"
COLOR_IDLE = "#858585"
COLOR_RUNNING = "#00b4d8"


def build_dark_qss(base_px: int = 13) -> str:
    """按基准字号 base_px 生成整套深色 QSS。"""
    b = max(10, min(24, base_px))
    title_size = b + 5
    tab_size = b
    btn_size = max(11, b - 1)
    primary_btn_size = b + 1
    input_size = b
    console_size = b
    section_size = max(11, b - 1)

    return f"""/* 基础窗口与容器 */
QMainWindow {{
    background-color: #1e1e1e;
}}

QWidget#dcc_checker_root {{
    background-color: #1e1e1e;
    color: #d4d4d4;
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", "Arial", sans-serif;
    font-size: {b}px;
}}

/* 标签页控件 */
QTabWidget::pane {{
    border: 1px solid #3e3e42;
    background-color: #252526;
    border-radius: 4px;
    top: -1px;
}}

QTabBar {{
    background-color: transparent;
}}

QTabBar::tab {{
    background-color: #2d2d2d;
    color: #9a9a9a;
    border: 1px solid #3a3a3a;
    border-bottom: none;
    padding: 8px 22px;
    margin-right: 4px;
    font-size: {tab_size}px;
    font-weight: 600;
    min-height: 20px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}

QTabBar::tab:hover {{
    background-color: #333333;
    color: #ffffff;
}}

QTabBar::tab:selected {{
    background-color: #252526;
    color: #ffffff;
    border-color: #3e3e42;
    border-bottom: 1px solid #252526;
}}

/* 基础按钮 */
QPushButton {{
    background-color: #333333;
    color: #e0e0e0;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 6px 14px;
    font-size: {btn_size}px;
    font-weight: 500;
    min-height: 20px;
}}

QPushButton:hover {{
    background-color: #3e3e42;
    color: #ffffff;
    border-color: #4f4f54;
}}

QPushButton:pressed {{
    background-color: #252526;
    border-color: #0e639c;
}}

QPushButton:disabled {{
    background-color: #252526;
    color: #606060;
    border-color: #333333;
}}

/* 主要操作按钮 (Run Selected Checks) */
QPushButton#primary_button {{
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #1177bb;
    border-radius: 4px;
    padding: 10px 20px;
    font-size: {primary_btn_size}px;
    font-weight: bold;
    min-height: 24px;
}}

QPushButton#primary_button:hover {{
    background-color: #1177bb;
    border-color: #1f8ad2;
}}

QPushButton#primary_button:pressed {{
    background-color: #0d5c90;
}}

/* 小型动作按钮 (Run, Refresh 等) */
QPushButton#icon_button {{
    background-color: #333333;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    padding: 4px 12px;
    font-size: {btn_size}px;
    min-height: 18px;
}}

QPushButton#icon_button:hover {{
    background-color: #3e3e42;
    border-color: #4f4f54;
    color: #ffffff;
}}

/* 输入框 */
QLineEdit {{
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: {input_size}px;
    min-height: 20px;
    selection-background-color: #094771;
}}

QLineEdit:focus {{
    border-color: #0e639c;
    color: #ffffff;
}}

/* 复选框 */
QCheckBox {{
    color: #e0e0e0;
    font-size: {b}px;
    spacing: 8px;
}}

QCheckBox:hover {{
    color: #ffffff;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    background-color: #1a1a1a;
}}

QCheckBox::indicator:hover {{
    border-color: #0e639c;
}}

QCheckBox::indicator:checked {{
    background-color: #0e639c;
    border-color: #1177bb;
}}

/* 文本控制台 */
QPlainTextEdit, QTextEdit {{
    background-color: #1a1a1a;
    color: #d4d4d4;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: {console_size}px;
    padding: 8px;
    line-height: 1.5;
}}

/* 列表与树形视图 */
QTreeWidget, QListWidget {{
    background-color: #1a1a1a;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 4px;
    font-size: {b}px;
}}

QTreeWidget::item, QListWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid #252526;
}}

QTreeWidget::item:hover, QListWidget::item:hover {{
    background-color: #2d2d2d;
    color: #ffffff;
}}

QTreeWidget::item:selected, QListWidget::item:selected {{
    background-color: #094771;
    color: #ffffff;
}}

QHeaderView::section {{
    background-color: #252526;
    color: #9a9a9a;
    padding: 6px 10px;
    border: none;
    border-bottom: 1px solid #3e3e42;
    font-size: {section_size}px;
    font-weight: bold;
}}

/* 滚动条 */
QScrollBar:vertical {{
    background-color: #1e1e1e;
    width: 10px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: #3e3e42;
    min-height: 24px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: #4f4f54;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: #1e1e1e;
    height: 10px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: #3e3e42;
    min-width: 24px;
    border-radius: 5px;
    margin: 2px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: #4f4f54;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* 分割条 */
QSplitter::handle {{
    background-color: #333333;
}}

QSplitter::handle:hover {{
    background-color: #0e639c;
}}

/* 工具提示 */
QToolTip {{
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    padding: 6px 10px;
    font-size: {max(11, b - 1)}px;
    border-radius: 4px;
}}
"""


# 兼容引用：默认 13px QSS
DARK_THEME_QSS = build_dark_qss(13)


def category_badge_style(is_checker: bool = True, base_px: int = 13) -> str:
    """生成类别/类型标签样式。"""
    sz = max(9, base_px - 2)
    if is_checker:
        return f"""
            QLabel {{
                background-color: #1b3a4b;
                color: #5bc0be;
                border: 1px solid #274c5e;
                border-radius: 3px;
                padding: 2px 7px;
                font-size: {sz}px;
                font-weight: bold;
            }}
        """
    else:
        return f"""
            QLabel {{
                background-color: #3a1518;
                color: #ff6b6b;
                border: 1px solid #5e2327;
                border-radius: 3px;
                padding: 2px 7px;
                font-size: {sz}px;
                font-weight: bold;
            }}
        """


def status_badge_style(status_color: str, base_px: int = 13) -> str:
    """生成状态指示标签样式。"""
    sz = max(10, base_px - 1)
    return f"""
        QLabel {{
            background-color: transparent;
            color: {status_color};
            font-size: {sz}px;
            font-weight: bold;
            padding: 2px 4px;
        }}
    """


def group_title_style(base_px: int = 13) -> str:
    """生成折叠分组标题行的 QSS 样式。"""
    return f"""
        QToolButton#group_title {{
            background-color: transparent;
            color: #ffffff;
            border: none;
            border-bottom: 1px solid {BORDER_DARK};
            border-radius: 0px;
            text-align: left;
            padding: 8px 10px;
            font-size: {base_px}px;
            font-weight: bold;
            min-height: 20px;
        }}
        QToolButton#group_title:hover {{
            background-color: {BG_CARD_HOVER};
            color: #ffffff;
        }}
    """
