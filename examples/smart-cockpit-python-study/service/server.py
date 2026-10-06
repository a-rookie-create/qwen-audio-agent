"""Service 提供哪些网络入口？对应原 CockpitServiceServer。
不同入口共用一个业务对象，协议解析统一用伪操作表示。
"""


class CockpitServiceServer:
    def start(self):
        service = CockpitService()
        HTTP挂载('/api/cockpit/state', service.snapshot)
        HTTP挂载('/api/cockpit/commands', service.execute)
        SSE挂载('/api/cockpit/events', service.subscribe)
        MCP挂载('/mcp/frontend', service, 前台工具目录)
        MCP挂载('/mcp/backend', service, 后台工具目录)
        # 技能列表、删除、重置等辅助接口在原实现中继续提供。
