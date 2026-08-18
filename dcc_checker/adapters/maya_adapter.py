"""Maya 适配层：唯一接触 ``maya.cmds`` 的地方。

工具只经 ``ctx.adapter`` 调这里的方法，不直接碰 cmds。
本模块依赖 Maya 运行时，只能在 Maya（或 mayapy standalone）内实例化使用；
单测请用 :class:`~dcc_checker.adapters.mock_adapter.MockAdapter`。
"""
from __future__ import annotations

from typing import List

import maya.cmds as cmds

from .base import BaseAdapter


class MayaAdapter(BaseAdapter):
    """基于 ``maya.cmds`` 的真实场景数据访问实现。"""

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
        """删除指定节点的构建历史。"""
        for node in nodes:
            if cmds.objExists(node):
                cmds.delete(node, constructionHistory=True)

    def freeze_transforms(self, nodes: List[str]) -> None:
        """冻结指定节点的变换（makeIdentity）。"""
        for node in nodes:
            if cmds.objExists(node):
                cmds.makeIdentity(
                    node, apply=True,
                    translate=True, rotate=True, scale=True, normal=False,
                )

    def selected_meshes(self) -> List[str]:
        """返回当前选中的网格变换节点名列表。"""
        return self.list_meshes(selected_only=True)
