"""业务工具经 MCP，网页工具经检索接口；接口实现可以被替换。"""
from agent.mcp_client import CockpitMcpTools
from framework_reference.extension_ports import WebRetrieval
from study_support import ToolDefinition, ToolResult


class CockpitAgentTools:
    def __init__(self, cockpit: CockpitMcpTools, retrieval: WebRetrieval) -> None:
        self.cockpit, self.retrieval = cockpit, retrieval

    def list(self) -> list[ToolDefinition]:
        return self.cockpit.list() + [
            ToolDefinition('web_search', '搜索演示资料', {'type': 'object'}, 'web', 'backend'),
            ToolDefinition('fetch_url', '读取演示资料', {'type': 'object'}, 'web', 'backend')]

    async def call(self, name: str, args: dict) -> ToolResult:
        if name not in {'web_search', 'fetch_url'}:
            return await self.cockpit.call(name, args)
        try:
            data = await self.retrieval.search(args['query']) if name == 'web_search' else await self.retrieval.fetch_url(args['url'])
            data['retrieval'] = {'tool': name}
            return ToolResult(data['content'], data)
        except ValueError as error:
            return ToolResult('检索失败：' + str(error), {'citations': []}, is_error=True)
