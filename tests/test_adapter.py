"""adapter 层安全纯函数测试（脱离 Maya）。"""
from dcc_checker.adapters.base import should_bake_history


def test_should_bake_history_skin_cluster():
    assert should_bake_history(["skinCluster"]) is True


def test_should_bake_history_blend_shape():
    assert should_bake_history(["blendShape"]) is True


def test_should_bake_history_both():
    assert should_bake_history(["skinCluster", "blendShape", "tweak"]) is True


def test_should_bake_history_plain():
    assert should_bake_history(["polyCube", "mesh", "polyMesh"]) is False


def test_should_bake_history_empty():
    assert should_bake_history([]) is False
