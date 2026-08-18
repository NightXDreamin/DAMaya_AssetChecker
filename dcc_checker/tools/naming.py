"""命名规范检测工具。"""
from dcc_checker.core.tool import BaseTool, ToolResult


class NamingPrefixTool(BaseTool):
    id = "naming.prefix"
    name = "命名前缀检查 (SM_/SK_)"
    category = "Naming"
    description = "网格必须带 SM_ 或 SK_ 前缀"
    is_checker = True

    PREFIXES = ("SM_", "SK_")

    def run(self, ctx):
        meshes = ctx.adapter.list_meshes()
        bad = [m for m in meshes if not m.startswith(self.PREFIXES)]
        if bad:
            return ToolResult.failed(
                ["缺少 SM_/SK_ 前缀的网格：%s" % m for m in bad]
            )
        return ToolResult.passed(["所有 %d 个网格前缀合规" % len(meshes)])
