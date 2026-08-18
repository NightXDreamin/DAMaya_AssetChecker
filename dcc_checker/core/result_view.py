"""红/绿语义与 log 文本渲染：把 :class:`ToolResult` 映射到 UI 表现。

与 Maya 无关，可单测。

* ``status_color`` —— 状态到颜色（绿/红）的映射
* ``render_log``    —— 把一次运行结果渲染成 log console 的文本行
"""
from __future__ import annotations

from typing import List

from .tool import ToolResult, ToolStatus

# PASS -> 绿；FAIL（有 Issue）/ ERROR（异常） -> 红
COLOR_BY_STATUS = {
    ToolStatus.PASS: "#2ecc71",  # 绿
    ToolStatus.FAIL: "#e74c3c",  # 红
    ToolStatus.ERROR: "#c0392b",  # 深红（异常）
}


def status_color(status: ToolStatus) -> str:
    """状态到颜色，供面板状态圆点使用。"""
    return COLOR_BY_STATUS.get(status, "#888888")


def render_log(tool_name: str, result: ToolResult) -> List[str]:
    """把一次运行结果渲染成 log console 的文本行。

    * 首行：``[PASS|FAIL|ERROR] <tool_name>``
    * FAIL：每条 Issue 详情一行
    * ERROR：messages 即 traceback 行，逐行输出
    """
    lines = ["[{}] {}".format(result.status.name, tool_name)]
    if result.messages:
        for msg in result.messages:
            for line in str(msg).splitlines():
                lines.append("    " + line)
    elif result.status is ToolStatus.PASS:
        lines.append("    ok")
    return lines
