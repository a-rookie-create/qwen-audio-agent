"""委派工具说明做什么？对应 spawn-thinking-tool.mjs。
它帮助前台模型选择路径，本身不执行任务。
"""


def create_cockpit_spawn_thinking_description(routing):
    return 根据实际工具归属生成说明(routing)
    # 前台领域直接调用；后台领域才委派。新闻研究也可交给后台。
    # 混合请求按归属拆分；多意图或多途经点不等于整句话都交给后台。
