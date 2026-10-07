"""后台 MCP 客户端：真实调用本地边界对象，能直接跳转到服务器方法。"""
from service.mcp_server import CockpitMcpServer
from study_support import ToolDefinition, ToolResult


class CockpitMcpTools:
    def __init__(self, server: CockpitMcpServer) -> None:
        self.server = server

    def list(self) -> list[ToolDefinition]:
        # 从已绑定的后台 MCP 面取得工具目录，不能看到前台专属车控等工具。
        return self.server.list_tools()

    async def call(self, name: str, arguments: dict) -> ToolResult:
        # 服务端再次检查工具面，然后调用 Service；客户端本身不直接修改业务状态。
        return await self.server.call_tool(name, arguments)
