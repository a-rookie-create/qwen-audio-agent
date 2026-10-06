"""真实的模型→工具→模型循环；预算、历史与失败状态均有实际实现。"""
from __future__ import annotations
import asyncio
import json
from typing import Callable
from agent.agent_history import AgentHistory
from agent.model import ChatModel
from agent.tools import CockpitAgentTools
from study_support import ToolResult, TraceLog


async def run_cockpit_agent(objective: str, history: list[dict], model: ChatModel,
                            tools: CockpitAgentTools, on_tool_call: Callable[[str], None]) -> ToolResult:
    definitions = tools.list()
    allowed = {tool.name for tool in definitions}
    messages = [*history, {'role': 'user', 'content': objective}]
    count = 0
    last = ToolResult('未取得操作结果')
    sources: dict[str, dict] = {}
    for index in range(10):
        final = index == 9 or count >= 32
        reply = await model.complete(messages, [] if final else definitions)
        if not reply.tool_calls:
            return ToolResult(reply.content, {**last.data, 'sources': list(sources.values())}, is_error=last.is_error)
        if final:
            return last                     # 最后一轮不再执行模型提出的新工具。
        messages.append({'role': 'assistant', 'content': reply.content or None, 'tool_calls': [
            {'id': call.id, 'type': 'function', 'function': {'name': call.name,
             'arguments': json.dumps(call.arguments, ensure_ascii=False)}} for call in reply.tool_calls]})
        for call in reply.tool_calls:
            if call.name not in allowed:
                raise ValueError('模型选择了未注册工具：' + call.name)
            if count >= 32:
                result = ToolResult('调用预算已用完，此调用未执行', is_error=True)
            else:
                count += 1
                on_tool_call(call.name)
                result = await tools.call(call.name, call.arguments)
            last = result
            for citation in result.data.get('citations', []):
                sources[citation['url']] = {**sources.get(citation['url'], {}), **citation}
            messages.append({'role': 'tool', 'name': call.name, 'tool_call_id': call.id,
                             'content': result.content, 'result': result})
    return last


class CockpitAgentExecutor:
    def __init__(self, model: ChatModel, tools: CockpitAgentTools, trace: TraceLog) -> None:
        self.model, self.tools, self.trace = model, tools, trace
        self.history = AgentHistory()
        self.executions: dict[str, asyncio.Task] = {}

    async def execute(self, task_id: str, objective: str, context_id: str,
                      on_progress: Callable[[str], None]) -> ToolResult:
        self.trace.record('Agent', 'execute', objective)
        work = asyncio.create_task(run_cockpit_agent(objective, self.history.messages(context_id),
                self.model, self.tools, lambda name: on_progress('正在执行：' + name)))
        self.executions[task_id] = work
        try:
            result = await asyncio.wait_for(work, timeout=600)
            self.history.append(context_id, objective, result.content)
            return result
        except asyncio.CancelledError:
            self.history.append(context_id, objective, '任务已取消，已执行操作需查询状态。')
            raise
        finally:
            self.executions.pop(task_id, None)

    def cancel_task(self, task_id: str) -> None:
        work = self.executions.get(task_id)
        if work:
            work.cancel()
