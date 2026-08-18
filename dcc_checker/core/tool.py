"""工具契约：ToolStatus / ToolResult / ToolContext / BaseTool。

所有可插拔工具都继承 :class:`BaseTool`，放在 ``tools/`` 目录下即会被
:class:`dcc_checker.core.registry.ToolRegistry` 自动发现。

本模块不依赖 Maya，可脱离 Maya 用 mock 数据做单元测试。
"""
from __future__ import annotations

import enum
from typing import List, Optional, Sequence


class ToolStatus(enum.Enum):
    """工具运行结果状态。

    * ``PASS``  —— 绿：运行成功（检测类工具表示无 Issue）。
    * ``FAIL``  —— 红：运行成功但结果不合格（检测类工具有 Issue）。
    * ``ERROR`` —— 红：运行过程中抛出异常（log 里附 traceback）。
    """

    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


class ToolResult:
    """一次 ``run()`` 的返回结果：状态 + 若干条信息（供 log console 展示）。"""

    def __init__(self, status: ToolStatus, messages: Optional[Sequence[str]] = None):
        self.status = status
        self.messages = list(messages or [])

    @classmethod
    def passed(cls, messages: Optional[Sequence[str]] = None) -> "ToolResult":
        return cls(ToolStatus.PASS, messages)

    @classmethod
    def failed(cls, messages: Optional[Sequence[str]] = None) -> "ToolResult":
        return cls(ToolStatus.FAIL, messages)

    @classmethod
    def errored(cls, messages: Optional[Sequence[str]] = None) -> "ToolResult":
        return cls(ToolStatus.ERROR, messages)

    @property
    def ok(self) -> bool:
        return self.status is ToolStatus.PASS

    @property
    def is_error(self) -> bool:
        return self.status is ToolStatus.ERROR

    def __repr__(self) -> str:  # pragma: no cover - 便于调试
        return "ToolResult({}, {} messages)".format(self.status.name, len(self.messages))


class ToolContext:
    """``BaseTool.run(ctx)`` 的运行时上下文。

    持有对 DCC 适配层的引用；检测逻辑只通过 ``ctx.adapter`` 拿数据，
    不直接 ``import maya.cmds``，从而可用 mock adapter 做单测。
    """

    def __init__(self, adapter=None, **extra):
        self.adapter = adapter
        self.extra = dict(extra)

    def __getattr__(self, name):
        # 允许把额外数据挂在 ctx 上（如 ctx.selected_only）
        try:
            return self.extra[name]
        except KeyError:
            raise AttributeError(name)


class BaseTool:
    """所有工具的抽象基类。

    子类只需：填写 ``id/name/category/description/is_checker`` 类属性，
    并实现 ``run(ctx) -> ToolResult``。放到 ``tools/`` 目录即插即用。
    """

    #: 全局唯一标识，如 ``"naming_prefix"``
    id: str = ""
    #: 面板显示名，如 ``"命名前缀检查 (SM_/SK_)"``
    name: str = ""
    #: 分组，如 ``"Naming"`` / ``"Cleanup"``
    category: str = "General"
    #: 单行描述，hover 提示用
    description: str = ""
    #: ``True`` 表示检测类工具（FAIL=有 Issue）；``False`` 表示动作类工具
    is_checker: bool = True

    @classmethod
    def tool_id(cls) -> str:
        """返回唯一 id，未显式填写时退化为类名。"""
        return cls.id or cls.__name__

    def run(self, ctx: ToolContext) -> ToolResult:
        """执行工具，返回 :class:`ToolResult`。子类必须实现。"""
        raise NotImplementedError

    def __repr__(self) -> str:  # pragma: no cover - 便于调试
        return "<{} {}>".format(type(self).__name__, self.tool_id())
