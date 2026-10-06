"""Gateway 如何接线？对应框架 createGatewayApplication。

工厂返回对象改写成教学类；不代表原项目提供这些 Python API。
"""


class GatewayApplication:
    def __init__(self, agent, config):
        # 启动时创建共用服务：任务管理、后台执行、前台工具接入。
        self.tasks = TaskManager()
        self.backend = BackendWorkRuntime(agent)
        self.task_operations = TaskOperations(self.tasks, self.backend)
        self.frontend_tools = 前台MCP接入(config)
        self.config = config

    def start(self):
        # HTTP/WebSocket 如何监听、认证、编解码，在伪代码中合成一步。
        监听客户端连接(self.on_client_connected)

    def on_client_connected(self, client):
        # 每条连接创建自己的会话，共用上面准备好的任务和工具服务。
        session = RealtimeSessionRuntime(
            client, self.task_operations, self.frontend_tools, self.config,
        )
        coordinator = SessionTaskCoordinator(self.tasks, session)
        连接会话与任务通知(session, coordinator)
        return session


def create_gateway_application(agent, config):
    return GatewayApplication(agent, config)
