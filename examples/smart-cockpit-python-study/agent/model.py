"""模型接口与可运行的离线模型；规则模型只用来演示工具循环，不冒充大模型。"""
from __future__ import annotations
import asyncio
import inspect
import json
from typing import Protocol
from study_support import ModelReply, ToolCall, ToolDefinition


# Protocol 只声明模型应提供的异步方法，运行时由 Demo 或外部适配器实际实现。
class ChatModel(Protocol):
    async def complete(self, messages: list[dict], tools: list[ToolDefinition]) -> ModelReply: ...


class DemoChatModel:
    def __init__(self, delay: float = 0.02) -> None:
        self.delay = delay

    async def complete(self, messages: list[dict], tools: list[ToolDefinition]) -> ModelReply:
        await asyncio.sleep(self.delay)  # 模拟网络等待，让前台能在后台执行时继续聊天。
        # 从消息末尾往前找最近的用户目标，避免历史任务的目标影响本次分支。
        objective = next(m['content'] for m in reversed(messages) if m['role'] == 'user')
        if not tools:
            # 执行器进入预算收尾轮时禁用工具，规则模型因此只返回文本。
            return ModelReply('已依据现有工具结果完成演示。')
        if messages[-1]['role'] != 'tool':
            # 首轮选择起点：明确确认走下单，咖啡走搜索，其他研究目标走网页搜索。
            if '确认下单' in objective:
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'confirm_order', 'confirmed': True})])
            if '咖啡' in objective or '拿铁' in objective:
                return ModelReply(tool_calls=[ToolCall('flashbuy', {'action': 'search', 'query': '咖啡'})])
            return ModelReply(tool_calls=[ToolCall('web_search', {'query': objective})])
        previous = messages[-1]
        # 后续轮次根据上一条真实工具结果推进，不一次性假设所有步骤已经成功。
        result = previous['result']
        if result.is_error:
            # 工具失败就报告错误，停止这个离线演示流程。
            return ModelReply(result.content)
        if previous['name'] == 'web_search':
            # 搜索得到引用后读取第一条页面，再生成带演示标记的简报。
            citations = result.data.get('citations', [])
            if citations:
                return ModelReply(tool_calls=[ToolCall('fetch_url', {'url': citations[0]['url']})])
        if previous['name'] == 'fetch_url':
            return ModelReply('离线演示简报：' + result.content + '（不是实时新闻）')
        if previous['name'] == 'flashbuy':
            # 状态驱动搜索 -> 加购 -> 预览；预览停下等待新一轮用户明确确认。
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
        # 去掉学习版 result 对象等内部字段，仅发送外部 Chat API 接受的消息字段。
        clean = [{k: v for k, v in m.items() if k in {'role', 'content', 'tool_calls', 'tool_call_id'}} for m in messages]
        # 将内部工具定义转成 API 的 function/schema 格式。
        definitions = [{'type': 'function', 'function': {'name': t.name,
                        'description': t.description, 'parameters': t.input_schema}} for t in tools]
        response = self.client.chat.completions.create(model=self.model, messages=clean, tools=definitions,
                                                       tool_choice='auto' if tools else 'none')
        if inspect.isawaitable(response):
            # 注入的客户端可能返回普通结果或可等待对象，两种返回方式都支持。
            response = await response
        message = response.choices[0].message
        # 将 JSON 参数字符串还原成字典，保留调用 ID，转换回执行器使用的数据类。
        calls = [ToolCall(c.function.name, json.loads(c.function.arguments or '{}'), c.id)
                 for c in message.tool_calls or []]
        return ModelReply(message.content or '', calls)
