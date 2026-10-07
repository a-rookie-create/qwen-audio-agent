"""进程内 MCP 边界模拟：真实目录过滤与工具执行；不实现线上 MCP 编解码。"""
from service.cockpit_service import CockpitService
from study_support import ToolDefinition, ToolResult


class CockpitMcpServer:
    def __init__(self, service: CockpitService, surface: str, cockpit_id: str = 'default') -> None:
        self.service, self.surface, self.cockpit_id = service, surface, cockpit_id

    def list_tools(self) -> list[ToolDefinition]:
        # surface 是 frontend/backend，注册表按它筛出当前边界可见的工具。
        return self.service.registry.definitions_for(self.surface)

    async def call_tool(self, name: str, arguments: dict) -> ToolResult:
        # 执行前再次检查目录，不能靠直接传名字越过前后台工具面的限制。
        if name not in {tool.name for tool in self.list_tools()}:
            return ToolResult('工具不在当前 MCP 面：' + name, is_error=True)
        # 工具面只控制接入，真实业务仍进入共享 Service。
        return await self.service.execute(name, arguments, self.cockpit_id)
