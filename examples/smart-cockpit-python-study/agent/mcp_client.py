"""后台怎样使用业务工具？对应 agent/mcp-client.mjs。
后台连接 /mcp/backend；前台连接另一个 /mcp/frontend。
"""


class CockpitMcpTools:
    def list(self):
        return MCP读取工具目录('/mcp/backend')

    def call(self, name, arguments):
        return MCP执行工具('/mcp/backend', name, arguments)
        # 业务操作在 Service 中执行，Agent 不自己保存车辆状态。
