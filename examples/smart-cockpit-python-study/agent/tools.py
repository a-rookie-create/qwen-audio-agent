"""业务工具经 MCP，网页工具经检索接口；接口实现可以被替换。"""
from agent.mcp_client import CockpitMcpTools
from framework_reference.extension_ports import WebRetrieval
from study_support import ToolDefinition, ToolResult


class CockpitAgentTools:
    def __init__(self, cockpit: CockpitMcpTools, retrieval: WebRetrieval) -> None:
        self.cockpit, self.retrieval = cockpit, retrieval

    def list(self) -> list[ToolDefinition]:
        # 合并后台业务工具与独立网页工具，模型看到的是统一的可调用目录。
        return self.cockpit.list() + [
            ToolDefinition('web_search', '搜索演示资料', {'type': 'object'}, 'web', 'backend'),
            ToolDefinition('fetch_url', '读取演示资料', {'type': 'object'}, 'web', 'backend')]

    async def call(self, name: str, args: dict) -> ToolResult:
        if name not in {'web_search', 'fetch_url'}:
            # 业务工具经 MCP 客户端到 Service，保持状态归业务服务管理。
            return await self.cockpit.call(name, args)
        try:
            # 网页工具走检索接口，不走业务 MCP；统一包装为同一种 ToolResult。
            data = await self.retrieval.search(args['query']) if name == 'web_search' else await self.retrieval.fetch_url(args['url'])
            data['retrieval'] = {'tool': name}
            return ToolResult(data['content'], data)
        except ValueError as error:
            # 用错误结果返回模型，让模型循环能根据失败信息停止或总结。
            return ToolResult('检索失败：' + str(error), {'citations': []}, is_error=True)
