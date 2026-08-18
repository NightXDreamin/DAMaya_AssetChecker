"""变换类动作工具。"""
from dcc_checker.core.tool import BaseTool, ToolResult


class FreezeTransformTool(BaseTool):
    id = "transform.freeze"
    name = "冻结变换 (Freeze Transforms)"
    category = "Transform"
    description = "冻结所有网格的变换（T/R/S 归零）"
    is_checker = False

    def run(self, ctx):
        meshes = ctx.adapter.list_meshes()
        ctx.adapter.freeze_transforms(meshes)
        return ToolResult.passed(["已冻结 %d 个网格的变换" % len(meshes)])
