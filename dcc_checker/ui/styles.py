"""UI 样式与主题定义模块。

提供深色工业风 QSS 样式表、状态颜色映射及视觉组件辅助。

所有控件 ``font-size`` 使用 ``em``（相对根基准字号），
通过 :func:`build_dark_qss(base_px)` 的 ``base_px`` 整体缩放，
可在面板 ``resizeEvent`` 中随窗口大小调整字号。
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
TEXT_NORMAL = "#cccccc"
TEXT_MUTED = "#858585"
TEXT_DIM = "#606060"

ACCENT_BLUE = "#0e639c"
ACCENT_BLUE_HOVER = "#1177bb"
ACCENT_BLUE_PRESSED = "#0d5c90"

COLOR_PASS = "#2ecc71"
COLOR_FAIL = "#e74c3c"
COLOR_ERROR = "#c0392b"
COLOR_IDLE = "#6c757d"
COLOR_RUNNING = "#00b4d8"


# 字体缩放基准
# 基准字号：面板高度在 BASE_HEIGHT 时所用根字号（px）
DEFAULT_FONT_PX = 13
MIN_FONT_PX = 11
MAX_FONT_PX = 17


def font_scale_for_height(panel_height: float) -> float:
    """根据面板高度返回字体缩放系数（相对 DEFAULT_FONT_PX）。

    * 高度 <= 400  => 0.80
    * 高度 >= 700  => 1.25
    * 之间线性映射
    """
    MIN_HEIGHT = 400.0
    BASE_HEIGHT = 700.0
    MIN_SCALE = 0.80
    MAX_SCALE = 1.25
    if panel_height <= MIN_HEIGHT:
        return MIN_SCALE
    if panel_height >= BASE_HEIGHT:
        return MAX_SCALE
    t = (panel_height - MIN_HEIGHT) / (BASE_HEIGHT - MIN_HEIGHT)
    return round(MIN_SCALE + t * (MAX_SCALE - MIN_SCALE), 4)


def build_dark_qss(base_px: int = DEFAULT_FONT_PX) -> str:
    """按基准字号 base_px（px）生成整套深色 QSS。

    根 ``QWidget#dcc_checker_root`` 的字号设为 ``base_px``，
    各控件用 ``em`` 相对它缩放。
    """
    base = base_px
    em = lambda n: "{}em".format(round(n / base, 3))

    return f"""/* 基础容器 */
QDockWidget {{
    background-color: #1e1e1e;
    color: #cccccc;
}}

QDockWidget::title {{
    background-color: #252526;
    padding: 6px 10px;
    border-bottom: 1px solid #333333;
    font-weight: bold;
    color: #ffffff;
}}

QWidget#dcc_checker_root {{
    background-color: #1e1e1e;
    color: #cccccc;
    font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", sans-serif;
    font-size: {base}px;
}}

/* 标签页控件 */
QTabWidget::pane {{
    border: 1px solid #3e3e42;
    background-color: #252526;
    border-radius: 3px;
}}

QTabBar::tab {{
    background-color: #2d2d2d;
    color: #858585;
    border: 1px solid #333333;
    border-bottom: none;
    padding: 6px 16px;
    margin-right: 2px;
    font-size: {em(11)};
    font-weight: 500;
    border-top-left-radius: 3px;
    border-top-right-radius: 3px;
}}

QTabBar::tab:hover {{
    background-color: #333333;
    color: #cccccc;
}}

QTabBar::tab:selected {{
    background-color: #252526;
    color: #ffffff;
    border-color: #3e3e42;
    border-bottom: 1px solid #252526;
}}

/* 按钮 */
QPushButton {{
    background-color: #333333;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    padding: 5px 12px;
    font-size: {em(12)};
    font-weight: 500;
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

/* 主要操作按钮 */
QPushButton#primary_button {{
    background-color: #0e639c;
    color: #ffffff;
    border: 1px solid #1177bb;
    border-radius: 3px;
    padding: 8px 16px;
    font-size: {em(13)};
    font-weight: bold;
}}

QPushButton#primary_button:hover {{
    background-color: #1177bb;
    border-color: #1f8ad2;
}}

QPushButton#primary_button:pressed {{
    background-color: #0d5c90;
}}

/* 小型动作按钮 */
QPushButton#icon_button {{
    background-color: transparent;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    padding: 3px 6px;
    font-size: {em(11)};
}}

QPushButton#icon_button:hover {{
    background-color: #333333;
    border-color: #4f4f54;
    color: #ffffff;
}}

/* 输入框 */
QLineEdit {{
    background-color: #1a1a1a;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: {em(12)};
    selection-background-color: #094771;
}}

QLineEdit:focus {{
    border-color: #0e639c;
    color: #ffffff;
}}

/* 下拉选择框 */
QComboBox {{
    background-color: #2d2d2d;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    padding: 4px 8px;
    font-size: {em(12)};
    min-width: 100px;
}}

QComboBox:hover {{
    background-color: #333333;
    border-color: #4f4f54;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid #3e3e42;
}}

QComboBox QAbstractItemView {{
    background-color: #252526;
    color: #cccccc;
    border: 1px solid #3e3e42;
    selection-background-color: #094771;
    selection-color: #ffffff;
}}

/* 复选框 */
QCheckBox {{
    color: #cccccc;
    font-size: {em(12)};
    spacing: 6px;
}}

QCheckBox:hover {{
    color: #ffffff;
}}

QCheckBox::indicator {{
    width: 14px;
    height: 14px;
    border: 1px solid #3e3e42;
    border-radius: 2px;
    background-color: #1a1a1a;
}}

QCheckBox::indicator:hover {{
    border-color: #0e639c;
}}

QCheckBox::indicator:checked {{
    background-color: #0e639c;
    border-color: #1177bb;
}}

/* 进度条 */
QProgressBar {{
    background-color: #1a1a1a;
    border: 1px solid #333333;
    border-radius: 3px;
    text-align: center;
    color: #ffffff;
    font-size: {em(11)};
    font-weight: bold;
}}

QProgressBar::chunk {{
    background-color: #0e639c;
    border-radius: 2px;
}}

/* 文本控制台 */
QPlainTextEdit, QTextEdit {{
    background-color: #1a1a1a;
    color: #b5b5b5;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: {em(12)};
    padding: 6px;
    line-height: 1.4;
}}

/* 列表与树形视图 */
QTreeWidget, QListWidget {{
    background-color: #1a1a1a;
    color: #cccccc;
    border: 1px solid #3e3e42;
    border-radius: 3px;
    font-size: {em(12)};
}}

QTreeWidget::item, QListWidget::item {{
    padding: 4px 6px;
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
    color: #858585;
    padding: 4px 8px;
    border: none;
    border-bottom: 1px solid #3e3e42;
    font-size: {em(11)};
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
    min-height: 20px;
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
    min-width: 20px;
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
    padding: 4px 8px;
    font-size: {em(12)};
    border-radius: 3px;
}}
"""


# 兼容旧引用：默认基准的整套 QSS
DARK_THEME_QSS = build_dark_qss(DEFAULT_FONT_PX)


def stat_card_style(border_color: str = BORDER_MID) -> str:
    """生成统计卡片的 QSS 样式。"""
    return f"""
        QFrame {{
            background-color: {BG_CARD};
            border: 1px solid {border_color};
            border-radius: 4px;
            padding: 3px 6px;
        }}
    """


def tool_card_style(is_hovered: bool = False) -> str:
    """生成工具卡片行的 QSS 样式。"""
    bg = BG_CARD_HOVER if is_hovered else BG_CARD
    return f"""
        QFrame#tool_card {{
            background-color: {bg};
            border: 1px solid {BORDER_DARK};
            border-radius: 4px;
            margin: 1px 0px;
        }}
    """


def category_badge_style(is_checker: bool = True) -> str:
    """生成类别/类型标签样式。"""
    if is_checker:
        return """
            QLabel {
                background-color: #1b3a4b;
                color: #5bc0be;
                border: 1px solid #274c5e;
                border-radius: 2px;
                padding: 1px 5px;
                font-size: 0.69em;
                font-weight: bold;
            }
        """
    else:
        return """
            QLabel {
                background-color: #3a2e1b;
                color: #f0a500;
                border: 1px solid #574426;
                border-radius: 2px;
                padding: 1px 5px;
                font-size: 0.69em;
                font-weight: bold;
            }
        """


def status_badge_style(status_color: str) -> str:
    """生成状态指示标签样式。"""
    return f"""
        QLabel {{
            background-color: transparent;
            color: {status_color};
            font-size: 0.77em;
            font-weight: bold;
            padding: 1px 4px;
        }}
    """


def group_title_style() -> str:
    """生成折叠分组标题行的 QSS 样式。"""
    return f"""
        QToolButton#group_title {{
            background-color: transparent;
            color: #e0e0e0;
            border: none;
            border-bottom: 1px solid {BORDER_DARK};
            border-radius: 0px;
            text-align: left;
            padding: 6px 8px;
            font-size: 0.92em;
            font-weight: bold;
        }}
        QToolButton#group_title:hover {{
            background-color: {BG_CARD_HOVER};
            color: #ffffff;
        }}
    """
