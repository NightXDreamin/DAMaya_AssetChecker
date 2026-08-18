"""ToolRunner 单测：顺序执行、异常转 ERROR、汇总报告。"""
from dcc_checker.core import (
    BaseTool,
    RunReport,
    ToolContext,
    ToolResult,
    ToolRunner,
    ToolStatus,
)


class _PassTool(BaseTool):
    id = "t.pass"
    name = "pass"

    def run(self, ctx):
        return ToolResult.passed(["ok"])


class _FailTool(BaseTool):
    id = "t.fail"
    name = "fail"

    def run(self, ctx):
        return ToolResult.failed(["issue found"])


class _BoomTool(BaseTool):
    id = "t.boom"
    name = "boom"

    def run(self, ctx):
        raise RuntimeError("kaboom")


def test_runner_executes_in_order():
    runner = ToolRunner(ctx=ToolContext(adapter=None))
    report = runner.run([_PassTool, _FailTool, _BoomTool, _PassTool])
    assert [r.tool_id for r in report.records] == ["t.pass", "t.fail", "t.boom", "t.pass"]


def test_runner_captures_exception_as_error():
    runner = ToolRunner()
    report = runner.run([_BoomTool])
    record = report.records[0]
    assert record.result.status is ToolStatus.ERROR
    assert record.result.is_error is True
    # messages 含异常信息与 traceback
    assert any("kaboom" in m for m in record.result.messages)
    assert any("Traceback" in m for m in record.result.messages)


def test_runner_summary_counts():
    runner = ToolRunner()
    report = runner.run([_PassTool, _PassTool, _FailTool, _BoomTool])
    assert report.summary() == {"total": 4, "pass": 2, "fail": 1, "error": 1}


def test_report_properties():
    report = RunReport([])
    assert report.passed == [] and report.failed == [] and report.errored == []
