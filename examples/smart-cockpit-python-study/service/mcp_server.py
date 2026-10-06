"""进程内 MCP 边界模拟：真实目录过滤与工具执行；不实现线上 MCP 编解码。"""
from service.cockpit_service import CockpitService
from study_support import ToolDefinition, ToolResult


class CockpitMcpServer:
    def __init__(self, service: CockpitService, surface: str, cockpit_id: str = 'default') -> None:
        self.service, self.surface, self.cockpit_id = service, surface, cockpit_id

    def list_tools(self) -> list[ToolDefinition]:
        return self.service.registry.definitions_for(self.surface)

    async def call_tool(self, name: str, arguments: dict) -> ToolResult:
        if name not in {tool.name for tool in self.list_tools()}:
            return ToolResult('工具不在当前 MCP 面：' + name, is_error=True)
        return await self.service.execute(name, arguments, self.cockpit_id)
