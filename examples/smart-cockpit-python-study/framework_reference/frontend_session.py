"""前台会话怎样处理三类请求？对应 realtime-session-runtime 与 ToolCallHandler。

前台 Agent 由实时模型、人设、上下文和工具共同构成；客户端负责 I/O。
方法与事件字段为思想表达，复杂协议转换已省略。
"""


class RealtimeSessionRuntime:
    def __init__(self, client, task_operations, tools, config):
        self.client = client
        self.task_operations = task_operations
        self.tools = tools
        self.model = 连接实时模型(config)  # 带人设、上下文、可用工具。
        self.tool_handler = ToolCallHandler(self)
        # 真实项目还将模型事件回调、客户端输入、播放回执接到当前会话。

    def on_user_audio(self, audio):
        self.model.send_audio(audio)       # 普通聊天从这里进入实时模型。

    def on_model_reply(self, reply):
        self.client.show_and_play(reply)  # 模型回复送回客户端展示、播放。

    def on_model_tool_call(self, name, arguments):
        return self.tool_handler.handle(name, arguments)

    def on_background_result(self, result):
        # 任务结果经通知/播报协调进入模型，由模型组织自然回复。
        等合适时机将结果送入模型(self.model, result)


class ToolCallHandler:
    def __init__(self, session):
        self.session = session

    def handle(self, name, arguments):
        if name == 'spawn_thinking':
            # 这里得到提交回执，不等待后台完成。
            task = self.session.task_operations.submit(arguments['objective'])
            result = {'status': 'accepted', 'task_id': task['id']}
        else:
            # 例如空调控制，经前台 MCP 调用 Service；这里等待工具结果。
            result = self.session.tools.execute(name, arguments)
        self.session.model.send_tool_result(result)
