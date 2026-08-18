"""设置对话框：提供界面字号滑杆调节与未来功能预留配置项。"""
from __future__ import annotations

import json
import os
from typing import Optional

from dcc_checker.ui.common import QtCore, QtGui, QtWidgets
from dcc_checker.ui.styles import (
    BG_CARD,
    BORDER_DARK,
    BORDER_MID,
    DARK_THEME_QSS,
    TEXT_MUTED,
    build_dark_qss,
)

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".damaya_asset_checker")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
DEFAULT_FONT_SIZE = 13


def load_user_config() -> dict:
    """加载用户偏好设置。"""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"font_size": DEFAULT_FONT_SIZE}


def save_user_config(cfg: dict) -> None:
    """持久化保存用户设置。"""
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


class SettingsDialog(QtWidgets.QDialog if QtWidgets is not None else object):  # type: ignore[misc]
    """设置对话框：字号实时滑杆与预留配置项。"""

    font_size_changed = QtCore.Signal(int) if QtCore is not None else None

    def __init__(self, parent=None, current_font_size: int = DEFAULT_FONT_SIZE):
        super().__init__(parent)
        self.setWindowTitle("DAMaya Asset Checker - Settings")
        self.setObjectName("dcc_checker_settings")
        self.resize(460, 360)
        self.setMinimumSize(400, 320)

        self._font_size = current_font_size
        self._cfg = load_user_config()

        self._build_ui()
        self.setStyleSheet(build_dark_qss(self._font_size))

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # 1. 标题
        title_lbl = QtWidgets.QLabel("Preferences & Settings")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title_lbl)

        # 2. 显示设置分组 (Appearance & Font Size)
        app_group = QtWidgets.QGroupBox("Appearance (界面与显示)")
        app_group.setStyleSheet(f"""
            QGroupBox {{
                color: #e0e0e0;
                font-weight: bold;
                border: 1px solid {BORDER_MID};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 14px;
                background-color: {BG_CARD};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }}
        """)
        app_layout = QtWidgets.QVBoxLayout(app_group)
        app_layout.setContentsMargins(12, 12, 12, 12)
        app_layout.setSpacing(10)

        # 字号滑杆行
        slider_row = QtWidgets.QHBoxLayout()
        slider_row.setSpacing(10)

        font_name_lbl = QtWidgets.QLabel("Font Size (字号大小):")
        font_name_lbl.setStyleSheet("color: #d4d4d4;")
        slider_row.addWidget(font_name_lbl)

        self.font_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal if QtCore else None)
        self.font_slider.setRange(11, 20)
        self.font_slider.setValue(self._font_size)
        self.font_slider.setTickInterval(1)
        self.font_slider.setSingleStep(1)
        self.font_slider.valueChanged.connect(self._on_slider_value_changed)
        slider_row.addWidget(self.font_slider, 1)

        self.font_val_label = QtWidgets.QLabel(f"{self._font_size} px")
        self.font_val_label.setFixedWidth(50)
        self.font_val_label.setStyleSheet("color: #00b4d8; font-weight: bold;")
        if QtCore is not None:
            self.font_val_label.setAlignment(QtCore.Qt.AlignCenter)
        slider_row.addWidget(self.font_val_label)

        reset_btn = QtWidgets.QPushButton("Reset")
        reset_btn.setObjectName("icon_button")
        reset_btn.setToolTip("重置为默认字号 (13px)")
        reset_btn.clicked.connect(self._on_reset_font)
        slider_row.addWidget(reset_btn)

        app_layout.addLayout(slider_row)

        hint_lbl = QtWidgets.QLabel("拖动滑杆可即时预览字号大小，适配不同 DPI 与屏幕分辨率。")
        hint_lbl.setStyleSheet("color: #858585; font-size: 11px;")
        app_layout.addWidget(hint_lbl)

        layout.addWidget(app_group)

        # 3. 预留设置分组 (Reserved Preferences)
        res_group = QtWidgets.QGroupBox("General (预留设置)")
        res_group.setStyleSheet(f"""
            QGroupBox {{
                color: #858585;
                font-weight: bold;
                border: 1px solid {BORDER_DARK};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 14px;
                background-color: {BG_CARD};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
            }}
        """)
        res_layout = QtWidgets.QVBoxLayout(res_group)
        res_layout.setContentsMargins(12, 12, 12, 12)
        res_layout.setSpacing(8)

        self.cb_autoscroll = QtWidgets.QCheckBox("Auto-scroll Log Console to latest output")
        self.cb_autoscroll.setChecked(True)
        res_layout.addWidget(self.cb_autoscroll)

        self.cb_switch_tab = QtWidgets.QCheckBox("Auto-switch to Issue Inspector on failure")
        self.cb_switch_tab.setChecked(True)
        res_layout.addWidget(self.cb_switch_tab)

        layout.addWidget(res_group)
        layout.addStretch()

        # 4. 底部关闭与保存按钮
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()

        close_btn = QtWidgets.QPushButton("Done (完成)")
        close_btn.setObjectName("primary_button")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)

        layout.addLayout(btn_row)

    def _on_slider_value_changed(self, value: int):
        self._font_size = value
        self.font_val_label.setText(f"{value} px")
        self.setStyleSheet(build_dark_qss(value))
        if self.font_size_changed:
            self.font_size_changed.emit(value)

        self._cfg["font_size"] = value
        save_user_config(self._cfg)

    def _on_reset_font(self):
        self.font_slider.setValue(DEFAULT_FONT_SIZE)
