"""示例工具单测：检测类与动作类，用 MockAdapter 脱离 Maya 验证。"""
from dcc_checker.adapters.mock_adapter import MockAdapter
from dcc_checker.core import ToolContext, ToolRunner, ToolStatus
from dcc_checker.core.registry import ToolRegistry
from dcc_checker.tools.cleanup import DeleteHistoryTool
from dcc_checker.tools.material import DefaultMaterialTool
from dcc_checker.tools.naming import NamingPrefixTool
from dcc_checker.tools.transform import FreezeTransformTool


def _ctx(meshes, shading=None):
    return ToolContext(adapter=MockAdapter(meshes=meshes, shading=shading))


def test_naming_prefix_detects_missing_prefix():
    ctx = _ctx(meshes=["SM_Rock", "pCube1"])
    res = NamingPrefixTool().run(ctx)
    assert res.status is ToolStatus.FAIL
    assert any("pCube1" in m for m in res.messages)


def test_naming_prefix_passes_when_all_prefixed():
    ctx = _ctx(meshes=["SM_Rock", "SK_Char"])
    res = NamingPrefixTool().run(ctx)
    assert res.status is ToolStatus.PASS


def test_default_material_detects_lambert1():
    ctx = _ctx(meshes=["SM_Rock"], shading={"SM_Rock": ["initialShadingGroup"]})
    res = DefaultMaterialTool().run(ctx)
    assert res.status is ToolStatus.FAIL


def test_default_material_passes_with_custom_material():
    ctx = _ctx(meshes=["SM_Rock"], shading={"SM_Rock": ["rockMat"]})
    res = DefaultMaterialTool().run(ctx)
    assert res.status is ToolStatus.PASS


def test_delete_history_calls_adapter():
    adapter = MockAdapter(meshes=["SM_Rock", "SK_Char"])
    res = DeleteHistoryTool().run(ToolContext(adapter=adapter))
    assert res.status is ToolStatus.PASS
    assert adapter.deleted_history == ["SM_Rock", "SK_Char"]


def test_freeze_transform_calls_adapter():
    adapter = MockAdapter(meshes=["SM_Rock"])
    res = FreezeTransformTool().run(ToolContext(adapter=adapter))
    assert res.status is ToolStatus.PASS
    assert adapter.frozen == ["SM_Rock"]


def test_registry_finds_all_example_tools():
    ids = set(t.tool_id() for t in ToolRegistry().refresh())
    expected = {
        "naming.prefix",
        "material.default",
        "cleanup.delete_history",
        "transform.freeze",
    }
    assert expected.issubset(ids)


def test_runner_runs_all_tools_end_to_end():
    adapter = MockAdapter(meshes=["pCube1"], shading={"pCube1": ["initialShadingGroup"]})
    ctx = ToolContext(adapter=adapter)
    classes = list(ToolRegistry().refresh())
    report = ToolRunner().run(classes, ctx=ctx)
    assert report.summary() == {"total": 4, "pass": 2, "fail": 2, "error": 0}
