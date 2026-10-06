"""MCP 层怎样接业务？对应 createCockpitMcpServer。
前后台暴露不同工具集合，但执行器和状态共用。
"""


class CockpitMcpServer:
    def __init__(self, service, allowed_tools):
        self.service, self.allowed_tools = service, allowed_tools

    def list_tools(self):
        return self.allowed_tools

    def call_tool(self, name, arguments):
        if name not in self.allowed_tools:
            return '此工具不在当前 MCP 面中'
        return self.service.execute(name, arguments)
