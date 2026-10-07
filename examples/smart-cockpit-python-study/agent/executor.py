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
    # 先固定本任务可用的工具名单，模型只能选择其中的工具。
    allowed = {tool.name for tool in definitions}
    # 展开历史消息，再追加本次目标；此列表用于本次模型/工具循环。
    messages = [*history, {'role': 'user', 'content': objective}]
    count = 0
    last = ToolResult('未取得操作结果')
    sources: dict[str, dict] = {}
    for index in range(10):
        # 最多十轮推理、三十二次实际工具调用；最后一轮不给工具，要求模型收尾。
        final = index == 9 or count >= 32
        reply = await model.complete(messages, [] if final else definitions)
        if not reply.tool_calls:
            # 模型没有请求新工具时结束；合并各轮引用，同时保留最后工具的错误标记。
            return ToolResult(reply.content, {**last.data, 'sources': list(sources.values())}, is_error=last.is_error)
        if final:
            return last                     # 最后一轮不再执行模型提出的新工具。
        messages.append({'role': 'assistant', 'content': reply.content or None, 'tool_calls': [
            {'id': call.id, 'type': 'function', 'function': {'name': call.name,
             'arguments': json.dumps(call.arguments, ensure_ascii=False)}} for call in reply.tool_calls]})
        for call in reply.tool_calls:
            # 记录 assistant 请求后逐个执行，后面的 tool 消息用 call.id 与请求对应。
            if call.name not in allowed:
                raise ValueError('模型选择了未注册工具：' + call.name)
            if count >= 32:
                # 同一轮可能给出多个调用；达到预算后仍补失败回执，但不再执行工具。
                result = ToolResult('调用预算已用完，此调用未执行', is_error=True)
            else:
                count += 1
                # 先报告将要调用的工具，实际业务结果必须等待 tools.call 返回。
                on_tool_call(call.name)
                result = await tools.call(call.name, call.arguments)
            last = result
            for citation in result.data.get('citations', []):
                # 按 URL 合并引用；后续 fetch 的 read 等信息可以补充先前 search 的记录。
                sources[citation['url']] = {**sources.get(citation['url'], {}), **citation}
            # 把真实结果放回消息列表，下一轮模型据此选择下一步，而非凭空宣称完成。
            # result 对象供离线模型使用；外部模型适配器会清理这个额外字段。
            messages.append({'role': 'tool', 'name': call.name, 'tool_call_id': call.id,
                             'content': result.content, 'result': result})
    return last


class CockpitAgentExecutor:
    def __init__(self, model: ChatModel, tools: CockpitAgentTools, trace: TraceLog) -> None:
        self.model, self.tools, self.trace = model, tools, trace
        self.history = AgentHistory()
        # task_id -> 正在跑模型循环的 Task，取消接口据此定位具体工作。
        self.executions: dict[str, asyncio.Task] = {}

    async def execute(self, task_id: str, objective: str, context_id: str,
                      on_progress: Callable[[str], None]) -> ToolResult:
        self.trace.record('Agent', 'execute', objective)
        # lambda 是进度回调：循环执行工具时才把工具名转换成进度文本。
        work = asyncio.create_task(run_cockpit_agent(objective, self.history.messages(context_id),
                self.model, self.tools, lambda name: on_progress('正在执行：' + name)))
        self.executions[task_id] = work
        try:
            # wait_for 对整段模型/工具循环设置十分钟上限，超时会取消内部 Task。
            result = await asyncio.wait_for(work, timeout=600)
            self.history.append(context_id, objective, result.content)
            return result
        except asyncio.CancelledError:
            # 保存取消事实后继续向上抛出，让 TaskManager 将任务标记为 cancelled。
            self.history.append(context_id, objective, '任务已取消，已执行操作需查询状态。')
            raise
        finally:
            # 成功、异常、超时、取消都移除活动记录，避免留下失效的取消目标。
            self.executions.pop(task_id, None)

    def cancel_task(self, task_id: str) -> None:
        work = self.executions.get(task_id)
        if work:
            work.cancel()
