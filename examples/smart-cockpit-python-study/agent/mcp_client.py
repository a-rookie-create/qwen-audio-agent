"""后台 MCP 客户端：真实调用本地边界对象，能直接跳转到服务器方法。"""
from service.mcp_server import CockpitMcpServer
from study_support import ToolDefinition, ToolResult


class CockpitMcpTools:
    def __init__(self, server: CockpitMcpServer) -> None:
        self.server = server

    def list(self) -> list[ToolDefinition]:
        return self.server.list_tools()

    async def call(self, name: str, arguments: dict) -> ToolResult:
        return await self.server.call_tool(name, arguments)
