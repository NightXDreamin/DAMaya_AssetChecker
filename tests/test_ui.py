"""UI 模块逻辑与样式单元测试。"""
from dcc_checker.core import ToolResult, ToolStatus
from dcc_checker.tools.naming import NamingPrefixTool
from dcc_checker.tools.cleanup import DeleteHistoryTool
from dcc_checker.ui import styles


def test_styles_constants():
    assert styles.BG_MAIN.startswith("#")
    assert styles.COLOR_PASS == "#2ecc71"
    assert styles.COLOR_FAIL == "#e74c3c"
    assert styles.COLOR_ERROR == "#c0392b"
    assert "QDockWidget" in styles.DARK_THEME_QSS
    assert "QPushButton" in styles.DARK_THEME_QSS


def test_style_helper_functions():
    badge_checker = styles.category_badge_style(is_checker=True)
    assert "#5bc0be" in badge_checker

    badge_action = styles.category_badge_style(is_checker=False)
    assert "#ff6b6b" in badge_action

    status_badge = styles.status_badge_style("#2ecc71")
    assert "color: #2ecc71;" in status_badge


def test_tool_filter_matching_logic():
    # 测试在脱离 Qt 界面环境下的搜索与分类匹配逻辑
    def match_tool(tool_cls, search_text, cat_filter):
        cat = getattr(tool_cls, "category", "General")
        if cat_filter and cat_filter != "All Categories" and cat != cat_filter:
            return False
        if not search_text:
            return True
        s = search_text.lower()
        t_id = tool_cls.tool_id().lower()
        t_name = (tool_cls.name or "").lower()
        t_desc = (getattr(tool_cls, "description", "") or "").lower()
        return s in t_id or s in t_name or s in t_desc or s in cat.lower()

    # NamingPrefixTool (category="Naming", name="命名前缀检查 (SM_/SK_)")
    assert match_tool(NamingPrefixTool, "naming", "All Categories") is True
    assert match_tool(NamingPrefixTool, "前缀", "All Categories") is True
    assert match_tool(NamingPrefixTool, "", "Naming") is True
    assert match_tool(NamingPrefixTool, "", "Cleanup") is False
    assert match_tool(NamingPrefixTool, "history", "Naming") is False

    # DeleteHistoryTool (category="Cleanup", name="删除构建历史")
    assert match_tool(DeleteHistoryTool, "history", "Cleanup") is True
    assert match_tool(DeleteHistoryTool, "SM_", "Cleanup") is False


def test_group_tools_by_category():
    from dcc_checker.ui.group_container import group_tools_by_category
    from dcc_checker.tools.transform import FreezeTransformTool

    tools = [NamingPrefixTool, DeleteHistoryTool, FreezeTransformTool, NamingPrefixTool]
    grouped = group_tools_by_category(tools)
    assert list(grouped.keys()) == ["Naming", "Cleanup", "Transform"]
    assert grouped["Naming"] == [NamingPrefixTool, NamingPrefixTool]  # 保持原顺序
    assert grouped["Cleanup"] == [DeleteHistoryTool]
    assert grouped["Transform"] == [FreezeTransformTool]


def test_group_tools_default_category():
    from dcc_checker.ui.group_container import group_tools_by_category

    class NoCat:
        pass

    grouped = group_tools_by_category([NoCat])
    assert "General" in grouped and NoCat in grouped["General"]


def test_reorder_cards_logic():
    from dcc_checker.ui.group_container import sort_cards_by_y

    # y 越小（越靠上）越靠前
    assert sort_cards_by_y({"a": 30, "b": 10, "c": 80}) == ["b", "a", "c"]


def test_font_scale_for_height():
    from dcc_checker.ui.styles import font_scale_for_height

    assert font_scale_for_height(350) == 0.8
    assert font_scale_for_height(700) == 1.25
    assert font_scale_for_height(1000) == 1.25
    assert 0.8 < font_scale_for_height(550) < 1.25


def test_build_dark_qss_changes_font_size():
    from dcc_checker.ui.styles import build_dark_qss

    assert "font-size: 13px" in build_dark_qss(13)
    assert "font-size: 16px" in build_dark_qss(16)
    assert build_dark_qss(13) != build_dark_qss(16)
