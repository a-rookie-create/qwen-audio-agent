"""模型接口与可运行的离线模型；规则模型只用来演示工具循环，不冒充大模型。"""
from __future__ import annotations
import asyncio
import inspect
import json
from typing import Protocol
from study_support import ModelReply, ToolCall, ToolDefinition


class ChatModel(Protocol):
    async def complete(self, messages: list[dict], tools: list[ToolDefinition]) -> ModelReply: ...


class DemoChatModel:
    def __init__(self, delay: float = 0.02) -> None:
        self.delay = delay

    async def complete(self, messages: list[dict], tools: list[ToolDefinition]) -> ModelReply:
        await asyncio.sleep(self.delay)  # 模拟网络等待，让前台能在后台执行时继续聊天。
        objective = next(m['content'] for m in reversed(messages) if m['role'] == 'user')
        if not tools:
            return ModelReply('已依据现有工具结果完成演示。')
        if messages[-1]['role'] != 'tool':
            if '确认下单' in objective:
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'confirm_order', 'confirmed': True})])
            if '咖啡' in objective or '拿铁' in objective:
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'search', 'query': '咖啡'})])
            return ModelReply(tool_calls=[ToolCall('web_search', {'query': objective})])
        previous = messages[-1]
        result = previous['result']
        if result.is_error:
            return ModelReply(result.content)
        if previous['name'] == 'web_search':
            citations = result.data.get('citations', [])
            if citations:
                return ModelReply(tool_calls=[ToolCall('fetch_url', {'url': citations[0]['url']})])
        if previous['name'] == 'fetch_url':
            return ModelReply('离线演示简报：' + result.content + '（不是实时新闻）')
        if previous['name'] == 'flashbuy':
            buy = result.data.get('flashbuy', {})
            if buy.get('status') == 'searched' and buy.get('results'):
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'add_to_cart', 'itemId': buy['results'][0]['id']})])
            if buy.get('status') == 'cart':
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'preview_order'})])
            if buy.get('status') == 'preview':
                return ModelReply('已准备演示订单预览，请明确确认是否下单。')
        return ModelReply(result.content)


class DashScopeCockpitModel:
    """可选模型适配器，需要用户注入自己的兼容客户端；默认演示不用它。"""
    def __init__(self, client, model: str = 'qwen3.8-flash') -> None:
        self.client, self.model = client, model

    async def complete(self, messages: list[dict], tools: list[ToolDefinition]) -> ModelReply:
        clean = [{k: v for k, v in m.items() if k in {'role', 'content', 'tool_calls', 'tool_call_id'}} for m in messages]
        definitions = [{'type': 'function', 'function': {'name': t.name,
                        'description': t.description, 'parameters': t.input_schema}} for t in tools]
        response = self.client.chat.completions.create(model=self.model, messages=clean, tools=definitions,
                                                       tool_choice='auto' if tools else 'none')
        if inspect.isawaitable(response):
            response = await response
        message = response.choices[0].message
        calls = [ToolCall(c.function.name, json.loads(c.function.arguments or '{}'), c.id)
                 for c in message.tool_calls or []]
        return ModelReply(message.content or '', calls)
