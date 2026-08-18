"""工具注册与发现：扫描 ``tools`` 包目录，收集所有 ``BaseTool`` 子类。

「实时刷新」的实现：``refresh()`` 重新遍历 ``tools/`` 目录并 ``importlib.reload``
每个工具模块，新增 / 修改的工具无需重启 Maya 即可出现在面板。
"""
from __future__ import annotations

import importlib
import inspect
import os
import pkgutil
from typing import List, Optional, Type

from .tool import BaseTool


class ToolRegistry:
    """扫描 ``dcc_checker.tools`` 包，发现所有 ``BaseTool`` 子类。"""

    def __init__(self, package_name: str = "dcc_checker.tools", tools_dir: Optional[str] = None):
        self.package_name = package_name
        self.tools_dir = tools_dir
        self._tools: List[Type[BaseTool]] = []
        self._loaded_modules = []

    def refresh(self) -> List[Type[BaseTool]]:
        """重新扫描并重载 tools 目录，返回按 (category, name) 排序的工具类列表。"""
        self._tools = []
        self._loaded_modules = []  # 清空旧模块引用，避免每次 refresh 累积内存
        package = importlib.import_module(self.package_name)
        tools_dir = self.tools_dir or os.path.dirname(package.__file__)

        for _finder, modname, _ispkg in pkgutil.iter_modules([tools_dir]):
            fullname = "{}.{}".format(self.package_name, modname)
            module = importlib.import_module(fullname)
            # 重载以支持「实时刷新」：工具文件改动后点 Refresh 即生效
            module = importlib.reload(module)
            self._loaded_modules.append(module)
            for _name, obj in inspect.getmembers(module, inspect.isclass):
                if obj is BaseTool:
                    continue
                if not issubclass(obj, BaseTool):
                    continue
                # 只收本模块直接定义的类，排除被 import 进来的基类等
                if obj.__module__ == fullname:
                    self._tools.append(obj)

        self._tools = sorted(self._tools, key=lambda c: (c.category, c.name))
        return list(self._tools)

    def list_tools(self) -> List[Type[BaseTool]]:
        """返回已发现的工具类（不触发扫描）。"""
        return list(self._tools)

    def get_tool(self, tool_id: str) -> Optional[Type[BaseTool]]:
        """按 id 查找工具类。"""
        for cls in self._tools:
            if cls.tool_id() == tool_id:
                return cls
        return None
