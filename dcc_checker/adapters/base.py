"""DCC 适配层抽象接口。

工具只通过 ``ctx.adapter`` 访问 DCC 场景，不直接 ``import maya.cmds``，
从而检测逻辑可脱离 Maya 用 mock 数据做单测。

* :class:`BaseAdapter` —— 接口契约
* :class:`~dcc_checker.adapters.maya_adapter.MayaAdapter` —— 真实实现（碰 cmds/OpenMaya）
* :class:`~dcc_checker.adapters.mock_adapter.MockAdapter` —— 内存实现（单测用）
"""
from __future__ import annotations

from typing import Iterable, List, Optional


def should_bake_history(deformer_node_types: Iterable[str]) -> bool:
    """判断某网格的变形器链是否需要「蒙皮保护」清理。

    若存在 ``skinCluster`` 或 ``blendShape``，裸 ``delete(constructionHistory=True)``
    会破坏蒙皮权重 / 变形目标，必须改用 ``bakePartialHistory`` 保守路径。
    纯函数，可脱离 Maya 单测。
    """
    protected = ("skinCluster", "blendShape")
    return any(t in protected for t in deformer_node_types)


class BaseAdapter:
    """工具可用的 DCC 数据访问接口。

    方法签名是「最小可用集」，随工具需求扩展。默认抛 :class:`NotImplementedError`，
    由具体实现覆盖。
    """

    # ---- 查询类 ----
    def list_meshes(self, selected_only: bool = False) -> List[str]:
        """返回场景中网格变换节点名列表（不含 shape 节点）。"""
        raise NotImplementedError

    def get_shading_engines(self, mesh: str) -> List[str]:
        """返回某网格绑定的着色引擎（材质）名列表。"""
        raise NotImplementedError

    # ---- 动作类 ----
    def delete_history(self, nodes: List[str]) -> None:
        """删除指定节点的构建历史。"""
        raise NotImplementedError

    def freeze_transforms(self, nodes: List[str]) -> None:
        """冻结指定节点的变换。"""
        raise NotImplementedError

    # ---- 可选：选中集 ----
    def selected_meshes(self) -> List[str]:
        """返回当前选中的网格变换节点名列表。"""
        raise NotImplementedError
