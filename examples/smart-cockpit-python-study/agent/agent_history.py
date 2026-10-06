"""后台怎样保留近期上下文？对应 agent/agent-history.mjs。
只保存请求/结果对，按 contextId 隔离；不是前台的长期记忆。
"""


class AgentHistory:
    def messages(self, context_id):
        return 读取此上下文的近期请求结果对(context_id)

    def append(self, context_id, request, reply):
        保存请求结果对(context_id, request, reply)
        限制历史长度和上下文数量()  # 原版最多 50 轮、100 个上下文。
