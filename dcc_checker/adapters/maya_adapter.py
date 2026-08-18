"""Maya 适配层：唯一接触 ``maya.cmds`` 的地方。

工具只经 ``ctx.adapter`` 调这里的方法，不直接碰 cmds。
本模块依赖 Maya 运行时，只能在 Maya（或 mayapy standalone）内实例化使用；
单测请用 :class:`~dcc_checker.adapters.mock_adapter.MockAdapter`。
"""
from __future__ import annotations

import contextlib
from typing import Iterator, List

import maya.cmds as cmds

from .base import BaseAdapter, should_bake_history


class MayaAdapter(BaseAdapter):
    """基于 ``maya.cmds`` 的真实场景数据访问实现。"""

    @contextlib.contextmanager
    def _undo_chunk(self) -> Iterator[None]:
        """把上下文内的操作合并为一个撤销单元（一次操作 = 一个 Ctrl+Z 单元）。"""
        cmds.undoInfo(openChunk=True, chunkName=self.__class__.__name__)
        try:
            yield
        finally:
            cmds.undoInfo(closeChunk=True)

    def _deformer_types(self, node: str) -> List[str]:
        """返回某网格变形链上的节点类型（用于蒙皮保护判定）。"""
        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True) or []
        types: List[str] = []
        for shp in shapes:
            history = cmds.listHistory(shp, pruneDagObjects=True) or []
            for h in history:
                if cmds.objExists(h):
                    types.append(cmds.nodeType(h))
        return types

    def list_meshes(self, selected_only: bool = False) -> List[str]:
        """返回场景中网格变换节点名列表（不含 shape、不含中间对象）。"""
        if selected_only:
            nodes = cmds.ls(selection=True, long=False) or []
        else:
            nodes = cmds.ls(type="transform", long=False) or []

        result: List[str] = []
        for node in nodes:
            shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                result.append(node)
        return result

    def get_shading_engines(self, mesh: str) -> List[str]:
        """返回某网格绑定的着色引擎（材质）名列表（去重）。"""
        shapes = cmds.listRelatives(mesh, shapes=True, noIntermediate=True) or []
        if not shapes:
            return []
        sgs = cmds.listConnections(shapes[0], type="shadingEngine") or []
        # 去重且保持顺序
        return list(dict.fromkeys(sgs))

    def delete_history(self, nodes: List[str]) -> None:
        """删除指定节点的构建历史。

        蒙皮保护：若节点带 ``skinCluster`` / ``blendShape``，改用
        ``bakePartialHistory`` 保守路径，绝不裸删历史破坏蒙皮权重。
        整体包裹为单一撤销单元。
        """
        with self._undo_chunk():
            for node in nodes:
                if not cmds.objExists(node):
                    continue
                if should_bake_history(self._deformer_types(node)):
                    try:
                        cmds.bakePartialHistory(node, prePostDeformers=True)
                    except Exception:
                        # 保守回退：宁可跳过也不破坏蒙皮
                        continue
                else:
                    cmds.delete(node, constructionHistory=True)

    def freeze_transforms(self, nodes: List[str]) -> None:
        """冻结指定节点的变换（makeIdentity），整体包裹为单一撤销单元。"""
        with self._undo_chunk():
            for node in nodes:
                if cmds.objExists(node):
                    cmds.makeIdentity(
                        node, apply=True,
                        translate=True, rotate=True, scale=True, normal=False,
                    )

    def selected_meshes(self) -> List[str]:
        """返回当前选中的网格变换节点名列表。"""
        return self.list_meshes(selected_only=True)
