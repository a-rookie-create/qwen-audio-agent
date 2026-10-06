"""后台 Agent 的核心思想：模型决定调用哪些工具，真实结果回到模型。

对应原 runCockpitAgent / CockpitAgentExecutor。
这里省略 Schema 转换、来源解析、超时控制和完整 A2A 事件。
"""


def run_cockpit_agent(objective, model, tools):
    messages = [{'role': 'user', 'content': objective}]
    for round_index in range(10):
        # 原版最多 10 个模型轮次，最后一轮禁用工具，依据真实结果收尾。
        available_tools = tools.list() if round_index < 9 else []
        reply = model.complete(messages, available_tools)
        messages.append(reply)
        if not reply.tool_calls:
            return reply.content          # 模型认为工作完成，返回回答。
        if round_index == 9:
            return 根据已取得结果诚实总结(messages)
        for call in reply.tool_calls:
            # 工具改变真实业务状态；不能用模型的口头承诺代替执行。
            result = tools.call(call.name, call.arguments)
            messages.append({'role': 'tool', 'content': result})
    # 原版另限制实际工具调用数为 32、单任务上限 10 分钟，本页不展开实现。


class CockpitAgentExecutor:
    def __init__(self, model, tools):
        self.model, self.tools = model, tools

    def execute(self, task, event_bus):
        event_bus.publish('working', task)
        try:
            result = run_cockpit_agent(task['objective'], self.model, self.tools)
            event_bus.publish('artifact', result)  # 详细结果。
            event_bus.publish('completed', result)
        except Exception as error:
            event_bus.publish('failed', str(error))
        # 历史、进度、取消与来源信息由原实现继续管理。
