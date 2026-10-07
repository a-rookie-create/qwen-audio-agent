"""后台短期上下文，只保留请求/回复；不等于前台长期记忆。"""
from copy import deepcopy
from collections import OrderedDict


class AgentHistory:
    def __init__(self, max_turns: int = 50, max_contexts: int = 100) -> None:
        self.max_turns, self.max_contexts = max_turns, max_contexts
        self.contexts: OrderedDict[str, list[dict]] = OrderedDict()

    def messages(self, context_id: str) -> list[dict]:
        # 为本次新目标预留一轮，只取最近 max_turns - 1 轮已完成历史。
        turns = self.contexts.get(context_id, [])[-(self.max_turns - 1):] if self.max_turns > 1 else []
        # 将每轮中的 user/assistant 消息展开为列表，返回副本保护已保存的历史。
        return deepcopy([m for turn in turns for m in turn['messages']])

    def append(self, context_id: str, request: str, reply: str) -> None:
        # 先取出旧记录再放到末尾，OrderedDict 的顺序表示最近写入的上下文顺序。
        turns = self.contexts.pop(context_id, [])
        turns.append({'messages': [{'role': 'user', 'content': request}, {'role': 'assistant', 'content': reply}]})
        self.contexts[context_id] = turns[-self.max_turns:]
        while len(self.contexts) > self.max_contexts:
            # 超过容量时淘汰最久没有写入新一轮的上下文，限制内存增长。
            self.contexts.popitem(last=False)
