"""工具执行器：按顺序运行勾选的工具，把异常转成 ERROR，返回结构化报告。"""
from __future__ import annotations

import traceback
from typing import List, Optional, Sequence, Type

from .tool import BaseTool, ToolContext, ToolResult, ToolStatus


class RunRecord:
    """单条工具的运行记录：工具类 + 运行结果。"""

    def __init__(self, tool_cls: Type[BaseTool], result: ToolResult):
        self.tool_cls = tool_cls
        self.result = result

    @property
    def tool_id(self) -> str:
        return self.tool_cls.tool_id()

    @property
    def tool_name(self) -> str:
        return self.tool_cls.name or self.tool_cls.tool_id()

    def __repr__(self) -> str:  # pragma: no cover
        return "RunRecord({}, {})".format(self.tool_id, self.result.status.name)


class RunReport:
    """一次批量运行的汇总报告。"""

    def __init__(self, records: Sequence[RunRecord]):
        self.records = list(records)

    @property
    def passed(self) -> List[RunRecord]:
        return [r for r in self.records if r.result.status is ToolStatus.PASS]

    @property
    def failed(self) -> List[RunRecord]:
        return [r for r in self.records if r.result.status is ToolStatus.FAIL]

    @property
    def errored(self) -> List[RunRecord]:
        return [r for r in self.records if r.result.status is ToolStatus.ERROR]

    def summary(self) -> dict:
        return {
            "total": len(self.records),
            "pass": len(self.passed),
            "fail": len(self.failed),
            "error": len(self.errored),
        }

    def __repr__(self) -> str:  # pragma: no cover
        return "RunReport({})".format(self.summary())


class ToolRunner:
    """顺序执行工具列表：勾选的工具按传入顺序逐个运行。

    任何 ``run()`` 抛出的异常都被捕获，转为 ``ToolStatus.ERROR`` 结果，
    messages 中包含异常信息与完整 traceback。
    """

    def __init__(self, ctx: Optional[ToolContext] = None):
        self.ctx = ctx or ToolContext()

    def run(self, tool_classes: Sequence[Type[BaseTool]],
            ctx: Optional[ToolContext] = None) -> RunReport:
        ctx = ctx or self.ctx
        records: List[RunRecord] = []
        for cls in tool_classes:
            tool = cls()
            try:
                result = tool.run(ctx)
            except Exception as exc:  # noqa: BLE001 - 兜底，任何工具异常都不中断批量运行
                result = ToolResult.errored([str(exc), traceback.format_exc()])
            records.append(RunRecord(cls, result))
        return RunReport(records)
