"""后台接入对象统一执行接口；本版 A2A 边界使用本地调用，不是线上协议实现。"""
from __future__ import annotations
from typing import Protocol, Callable, TYPE_CHECKING
from agent.server import CockpitAgentServer
from study_support import ToolResult, TraceLog
if TYPE_CHECKING:
    from framework_reference.task_runtime import TaskRecord


# Protocol 描述调用契约，省略号是接口声明；真正执行的是下面的具体适配器。
class BackendPort(Protocol):
    async def submit(self, task: TaskRecord, on_progress: Callable[[str], None]) -> ToolResult: ...
    def cancel(self, task_id: str) -> None: ...


class A2ABackendAdapter:
    def __init__(self, server: CockpitAgentServer, trace: TraceLog) -> None:
        self.server, self.trace = server, trace

    def describe(self) -> dict:
        return {'protocol': 'a2a-boundary-demo', 'configured': True, 'transport': 'in-process'}

    async def submit(self, task: TaskRecord, on_progress: Callable[[str], None]) -> ToolResult:
        self.trace.record('A2A Adapter', 'submit', task.id)
        # 把 Gateway 任务转换成 Agent 参数，用用户 + 会话标识隔离后台历史上下文。
        return await self.server.submit(task.id, task.objective,
                    task.owner_id + ':' + task.session_id, on_progress)

    def cancel(self, task_id: str) -> None:
        # 取消请求逐层传到执行器保存的 asyncio Task。
        self.server.cancel(task_id)

    def status(self, task_id: str) -> ToolResult | None:
        # 这里只查询 Agent 缓存的执行结果；queued/running 等状态归 Gateway 管理。
        return self.server.results.get(task_id)


def create_backend_agent_host(adapter: A2ABackendAdapter) -> A2ABackendAdapter:
    # 原 Host 加接口校验和宿主信息；此学习版保留可执行的提交/取消接线。
    return adapter


class BackendWorkRuntime:
    def __init__(self, agent: BackendPort) -> None:
        self.agent = agent

    async def run(self, task: TaskRecord, on_progress: Callable[[str], None]) -> ToolResult:
        result = await self.agent.submit(task, on_progress)
        # 把工具结果中的错误标记转换成异常，让 TaskManager 进入 failed 分支。
        if result.is_error:
            raise RuntimeError(result.content)
        return result

    def cancel(self, task_id: str) -> None:
        self.agent.cancel(task_id)
