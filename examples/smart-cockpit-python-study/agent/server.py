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
        return {'name': 'Python Study Agent', 'transport': 'in-process', 'streaming': True}

    async def submit(self, task_id: str, objective: str, context_id: str,
                     on_progress: Callable[[str], None]) -> ToolResult:
        result = await self.executor.execute(task_id, objective, context_id, on_progress)
        self.results[task_id] = result
        return result

    def cancel(self, task_id: str) -> None:
        self.executor.cancel_task(task_id)


def start_cockpit_agent_server(executor: CockpitAgentExecutor) -> CockpitAgentServer:
    return CockpitAgentServer(executor)
