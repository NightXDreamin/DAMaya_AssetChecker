"""示例工具：一个总是通过的探针，用于验证 ToolRegistry 的发现机制。"""
from dcc_checker.core.tool import BaseTool, ToolResult


class ProbePassTool(BaseTool):
    id = "example.probe_pass"
    name = "探针工具（总是通过）"
    category = "Example"
    description = "验证工具发现与批量运行的最小示例"
    is_checker = False

    def run(self, ctx):
        return ToolResult.passed(["探针工具运行成功，无异常。"])
