"""core 层基础单测：ToolStatus / ToolResult / 红绿语义 / registry 发现。"""
from dcc_checker.core import (
    BaseTool,
    ToolContext,
    ToolResult,
    ToolStatus,
    render_log,
    status_color,
)
from dcc_checker.core.registry import ToolRegistry


def test_tool_status_values():
    assert [s.value for s in ToolStatus] == ["pass", "fail", "error"]


def test_tool_result_factories():
    assert ToolResult.passed().ok is True
    assert ToolResult.failed().ok is False
    assert ToolResult.failed().is_error is False
    assert ToolResult.errored().is_error is True


def test_status_color_mapping():
    assert status_color(ToolStatus.PASS) != status_color(ToolStatus.FAIL)
    assert status_color(ToolStatus.PASS).startswith("#2e")  # 绿
    assert status_color(ToolStatus.FAIL).startswith("#e7")  # 红
    assert status_color(ToolStatus.ERROR).startswith("#c0")  # 深红


def test_render_log_fail_lists_issues():
    lines = render_log("命名前缀检查", ToolResult.failed(["SM 前缀缺失: pCube1"]))
    assert lines[0].startswith("[FAIL]")
    assert any("pCube1" in l for l in lines)


def test_render_log_error_keeps_traceback():
    lines = render_log("冻结", ToolResult.errored(["Traceback", "RuntimeError: boom"]))
    assert lines[0].startswith("[ERROR]")
    assert any("RuntimeError: boom" in l for l in lines)


def test_registry_discovers_naming():
    reg = ToolRegistry()
    ids = [t.tool_id() for t in reg.refresh()]
    assert "naming.prefix" in ids
    # probe 已迁移到 examples/，不应再被发现
    assert "example.probe_pass" not in ids


def test_tool_runs_with_mock_adapter():
    from dcc_checker.adapters.mock_adapter import MockAdapter

    class MeshCountTool(BaseTool):
        id = "probe.mesh_count"

        def run(self, ctx):
            meshes = ctx.adapter.list_meshes()
            return ToolResult.passed(["共 %d 个网格" % len(meshes)])

    ctx = ToolContext(adapter=MockAdapter(meshes=["SM_Rock", "SK_Char"]))
    res = MeshCountTool().run(ctx)
    assert res.ok is True
    assert "2" in res.messages[0]
