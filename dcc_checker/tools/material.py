"""材质检测工具。"""
from dcc_checker.core.tool import BaseTool, ToolResult


class DefaultMaterialTool(BaseTool):
    id = "material.default"
    name = "默认材质检查 (lambert1)"
    category = "Material"
    description = "网格不应使用 initialShadingGroup / lambert1 默认材质"
    is_checker = True

    DEFAULT_SGS = ("initialShadingGroup",)

    def run(self, ctx):
        meshes = ctx.adapter.list_meshes()
        bad = []
        for m in meshes:
            sgs = ctx.adapter.get_shading_engines(m)
            if not sgs or all(sg in self.DEFAULT_SGS for sg in sgs):
                bad.append(m)
        if bad:
            return ToolResult.failed(["使用默认材质的网格：%s" % m for m in bad])
        return ToolResult.passed(["所有 %d 个网格均已分配自定义材质" % len(meshes)])
