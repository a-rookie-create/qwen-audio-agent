"""怎样将后台 Agent 暴露给 Gateway？对应 agent/server.mjs。
A2A 服务接收任务，执行器负责模型循环；不是另一套实时语音会话。
"""


def start_cockpit_agent_server():
    model = DashScopeCockpitModel(模型客户端)
    tools = CockpitAgentTools(后台MCP接入, 网页检索能力)
    executor = CockpitAgentExecutor(model, tools)
    # A2A 请求先转换为执行器需要的任务；编码、流式状态等由协议层处理。
    启动A2A服务(任务处理器=executor.execute)
    发布AgentCard()  # Gateway 通过这个描述发现后台接口与能力。
