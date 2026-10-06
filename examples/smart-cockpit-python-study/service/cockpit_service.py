"""业务操作在哪里执行？对应原 CockpitService。

面板 HTTP 命令、前台 MCP、后台 MCP 最终共用同一个 execute。
"""


class CockpitService:
    def __init__(self):
        self.state = CockpitStateStore()   # 车辆、音乐、路线等业务事实。
        self.tools = ToolRegistry()       # 工具名称 → 对应的领域执行函数。

    def execute(self, tool_name, arguments):
        # 例如车控工具修改状态；导航工具调用地图服务并更新路线。
        result = self.tools.execute(tool_name, arguments, self.state)
        return result

    def snapshot(self):
        return self.state.snapshot()

    def subscribe(self, client):
        通过SSE向客户端发送状态变化(self.state, client)
        # UI 的状态订阅直接连 Service，不经过 Gateway。
