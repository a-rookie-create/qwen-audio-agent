"""进程内 A2A 边界：接收工作，调用执行器，记录结果；不实现线上 A2A 传输。"""
from __future__ import annotations
from typing import Callable
from agent.executor import CockpitAgentExecutor
from study_support import ToolResult


class CockpitAgentServer:
    def __init__(self, executor: CockpitAgentExecutor) -> None:
        self.executor = executor
        self.results: dict[str, ToolResult] = {}

    def agent_card(self) -> dict:
        # 描述本地 Agent 的能力边界，不在这里启动线上 A2A 网络服务。
        return {'name': 'Python Study Agent', 'transport': 'in-process', 'streaming': True}

    async def submit(self, task_id: str, objective: str, context_id: str,
                     on_progress: Callable[[str], None]) -> ToolResult:
        # 等执行器返回才缓存结果；若抛异常，则交由 Gateway 任务层记录失败。
        result = await self.executor.execute(task_id, objective, context_id, on_progress)
        self.results[task_id] = result
        return result

    def cancel(self, task_id: str) -> None:
        # 只转交取消请求，queued/running/cancelled 等任务状态仍由 TaskManager 决定。
        self.executor.cancel_task(task_id)


def start_cockpit_agent_server(executor: CockpitAgentExecutor) -> CockpitAgentServer:
    # 学习版的“启动”是创建本地边界对象，不启动子进程或监听端口。
    return CockpitAgentServer(executor)
