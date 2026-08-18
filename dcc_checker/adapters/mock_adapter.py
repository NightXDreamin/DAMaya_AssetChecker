"""内存版 adapter，用于脱离 Maya 的单元测试与命令行演示。

与 Maya 无关，纯内存记录调用，供 pytest 断言工具行为。
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .base import BaseAdapter


class MockAdapter(BaseAdapter):
    """可配置的假 adapter：传入网格列表与材质映射，记录动作调用。"""

    def __init__(self, meshes: Optional[List[str]] = None,
                 shading: Optional[Dict[str, List[str]]] = None):
        self.meshes = list(meshes or [])
        self.shading = dict(shading or {})  # mesh -> [shading engine, ...]
        self.deleted_history: List[str] = []
        self.frozen: List[str] = []

    def list_meshes(self, selected_only: bool = False) -> List[str]:
        return list(self.meshes)

    def get_shading_engines(self, mesh: str) -> List[str]:
        return list(self.shading.get(mesh, []))

    def delete_history(self, nodes: List[str]) -> None:
        self.deleted_history.extend(nodes)

    def freeze_transforms(self, nodes: List[str]) -> None:
        self.frozen.extend(nodes)

    def selected_meshes(self) -> List[str]:
        return list(self.meshes)  # 简化：mock 下选中集即全部
