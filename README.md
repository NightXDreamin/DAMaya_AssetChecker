# DCC Asset Checker — Maya 可插拔工具框架

Maya 端「提交前」资产合规检查器 + 可插拔工具 dock 面板。

工具以 `BaseTool` 子类形式放进 `tools/` 目录即插即用；在 Maya 顶部菜单呼出现代化深色 dock 面板，支持实时搜索、按类别折叠分组、组内拖拽排序、单工具独立测试与批量运行，提供彩色时间戳日志以及场景问题对象视口联动检查器。

## 环境要求

| 目标 | 版本 |
|---|---|
| Maya | 2022-2024 (Python 3.7-3.10 / PySide2) 或 2025+ (Python 3.11+ / PySide6) |
| 单测 | 系统 Python 3.x + pytest |

## 在 Maya 中加载

### 方式一：自动挂载（推荐，开 Maya 即出菜单）

运行一次安装脚本，把 hook 写进 Maya 的 `userSetup.py`：

```bash
python scripts/install_maya_setup.py
```

重启 Maya 后，主菜单栏自动出现 `DCC Checker → Open Tool Dock`。脚本幂等，可重复运行。

### 方式二：手动加载（单次生效）

打开 Maya Script Editor（Python 标签页），执行：

```python
import sys
sys.path.insert(0, r"<本仓库绝对路径>")

from dcc_checker.ui import main_menu
main_menu.install()
```

> 卸载菜单：`main_menu.uninstall()`

## 如何新增一个工具

在 `dcc_checker/tools/` 新建一个 `.py` 文件：

```python
from dcc_checker.core.tool import BaseTool, ToolResult


class MyTool(BaseTool):
    id = "my.example"
    name = "我的示例工具"
    category = "MyCategory"
    description = "这是一条示例工具"
    is_checker = True  # 检测类（FAIL=有 Issue）；动作类设 False

    def run(self, ctx):
        meshes = ctx.adapter.list_meshes()  # 经 adapter 拿数据，不直接 import maya.cmds
        if not meshes:
            return ToolResult.failed(["场景中没有网格"])
        return ToolResult.passed(["共 %d 个网格" % len(meshes)])
```

回到面板点 `Refresh`，新工具即出现。

## 运行测试

```bash
python -m pytest tests/ -q
```