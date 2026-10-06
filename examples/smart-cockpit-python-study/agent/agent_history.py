"""后台短期上下文，只保留请求/回复；不等于前台长期记忆。"""
from copy import deepcopy
from collections import OrderedDict


class AgentHistory:
    def __init__(self, max_turns: int = 50, max_contexts: int = 100) -> None:
        self.max_turns, self.max_contexts = max_turns, max_contexts
        self.contexts: OrderedDict[str, list[dict]] = OrderedDict()

    def messages(self, context_id: str) -> list[dict]:
        turns = self.contexts.get(context_id, [])[-(self.max_turns - 1):] if self.max_turns > 1 else []
        return deepcopy([m for turn in turns for m in turn['messages']])

    def append(self, context_id: str, request: str, reply: str) -> None:
        turns = self.contexts.pop(context_id, [])
        turns.append({'messages': [{'role': 'user', 'content': request}, {'role': 'assistant', 'content': reply}]})
        self.contexts[context_id] = turns[-self.max_turns:]
        while len(self.contexts) > self.max_contexts:
            self.contexts.popitem(last=False)
