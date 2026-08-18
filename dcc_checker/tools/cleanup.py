"""清理类动作工具。"""
from dcc_checker.core.tool import BaseTool, ToolResult


class DeleteHistoryTool(BaseTool):
    id = "cleanup.delete_history"
    name = "删除构建历史 (Delete History)"
    category = "Cleanup"
    description = "删除所有网格的构建历史"
    is_checker = False

    def run(self, ctx):
        meshes = ctx.adapter.list_meshes()
        ctx.adapter.delete_history(meshes)
        return ToolResult.passed(["已删除 %d 个网格的构建历史" % len(meshes)])
