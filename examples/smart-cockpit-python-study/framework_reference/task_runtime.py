"""真正的后台任务与通知：状态归 TaskManager，前台会话只观察并展示。"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable, TYPE_CHECKING
from uuid import uuid4
from study_support import Signal, ToolResult, TraceLog
from framework_reference.backend_adapter import BackendWorkRuntime
if TYPE_CHECKING:
    from framework_reference.frontend_session import RealtimeSessionRuntime


@dataclass
class TaskRecord:
    id: str
    objective: str
    owner_id: str
    session_id: str
    status: str = 'queued'
    notification: str = 'none'
    result: ToolResult | None = None
    work: asyncio.Task | None = None
    finished: asyncio.Event = field(default_factory=asyncio.Event)

    def snapshot(self) -> dict:
        return {'id': self.id, 'objective': self.objective, 'ownerId': self.owner_id,
                'sessionId': self.session_id, 'status': self.status,
                'notification': self.notification,
                'result': self.result.content if self.result else None}


class TaskManager:
    def __init__(self, trace: TraceLog) -> None:
        self.trace = trace
        self.tasks: dict[str, TaskRecord] = {}
        self.events = Signal()
        self.owner_locks: dict[str, asyncio.Lock] = {}

    def create(self, objective: str, owner_id: str, session_id: str,
               runner: Callable[[TaskRecord], Awaitable[ToolResult]]) -> TaskRecord:
        task = TaskRecord(uuid4().hex, objective, owner_id, session_id)
        self.tasks[task.id] = task
        self.emit('task.accepted', task)
        task.work = asyncio.create_task(self._execute(task, runner))
        return task  # 创建记录后就返回，不等待模型工具循环。

    async def _execute(self, task: TaskRecord, runner: Callable) -> None:
        try:
            lock = self.owner_locks.setdefault(task.owner_id, asyncio.Lock())
            async with lock:  # 同一个用户的后台工作依次运行。
                task.status = 'running'
                self.emit('task.running', task)
                result = await runner(task)
                self._finish(task, 'completed', result)
        except asyncio.CancelledError:
            self._finish(task, 'cancelled', ToolResult('已取消，已执行操作不会自动回滚。'))
        except Exception as error:
            self._finish(task, 'failed', ToolResult(str(error), is_error=True))

    def _finish(self, task: TaskRecord, status: str, result: ToolResult) -> None:
        task.status, task.result = status, result
        self.emit('task.' + status, task)
        if status in {'completed', 'failed'}:
            task.notification = 'pending'
            self.emit('task.notification.pending', task)
        task.finished.set()

    def emit(self, event_type: str, task: TaskRecord, message: str = '') -> None:
        self.trace.record('TaskManager', event_type, task.id)
        self.events.emit({'type': event_type, 'task': task.snapshot(), 'message': message})

    def get(self, task_id: str, owner_id: str) -> TaskRecord:
        task = self.tasks[task_id]
        if task.owner_id != owner_id:
            raise PermissionError('不能读取其他用户的任务')
        return task

    async def wait(self, task_id: str, owner_id: str) -> TaskRecord:
        task = self.get(task_id, owner_id)
        await task.finished.wait()
        return task

    async def cancel(self, task_id: str, owner_id: str) -> None:
        task = self.get(task_id, owner_id)
        if task.status in {'completed', 'failed', 'cancelled'}:
            return
        if task.work:
            task.work.cancel()
            await asyncio.gather(task.work, return_exceptions=True)
        if not task.finished.is_set():  # 处理协程尚未开始就被取消的情形。
            self._finish(task, 'cancelled', ToolResult('排队任务已取消'))

    def mark_delivered(self, task_id: str, owner_id: str) -> None:
        task = self.get(task_id, owner_id)
        if task.notification == 'delivering':
            task.notification = 'delivered'
            self.emit('task.notification.delivered', task)

    async def close(self) -> None:
        for task in tuple(self.tasks.values()):
            await self.cancel(task.id, task.owner_id)


class TaskOperations:
    def __init__(self, tasks: TaskManager, backend: BackendWorkRuntime) -> None:
        self.tasks, self.backend = tasks, backend

    def submit(self, objective: str, owner_id: str, session_id: str) -> TaskRecord:
        async def runner(task: TaskRecord) -> ToolResult:
            return await self.backend.run(task, lambda message: self.tasks.emit('task.progress', task, message))
        return self.tasks.create(objective, owner_id, session_id, runner)

    async def cancel(self, task_id: str, owner_id: str) -> None:
        self.tasks.get(task_id, owner_id)
        self.backend.cancel(task_id)
        await self.tasks.cancel(task_id, owner_id)


class SessionTaskCoordinator:
    def __init__(self, tasks: TaskManager, session: RealtimeSessionRuntime) -> None:
        self.tasks, self.session = tasks, session
        self.pending: set[str] = set()
        self.deliveries: set[asyncio.Task] = set()
        self.closed = False
        self.unsubscribe = tasks.events.subscribe(self.on_event)

    def on_event(self, event: dict) -> None:
        snapshot = event['task']
        if (snapshot['ownerId'], snapshot['sessionId']) != (self.session.owner_id, self.session.session_id):
            return
        self.session.send(event)  # 任务进度与聊天回复都是客户端可观察事件。
        if event['type'] == 'task.notification.pending':
            self.pending.add(snapshot['id'])
            self.refresh()

    def refresh(self) -> None:
        if self.closed or not self.session.can_announce():
            return
        for task_id in tuple(self.pending):
            task = self.tasks.get(task_id, self.session.owner_id)
            if task.notification == 'pending':
                task.notification = 'delivering'
                work = asyncio.create_task(self._deliver(task))
                self.deliveries.add(work)
                work.add_done_callback(self.deliveries.discard)

    async def _deliver(self, task: TaskRecord) -> None:
        delivered = await self.session.present_task_result(task)
        if not delivered:
            task.notification = 'pending'
        if task.notification == 'delivered':
            self.pending.discard(task.id)

    async def flush(self) -> None:
        self.refresh()
        while self.deliveries:
            batch = tuple(self.deliveries)
            await asyncio.gather(*batch)
            # 已完成 future 的 gather 可能不让出事件循环；不能只等 done 回调清理集合。
            self.deliveries.difference_update(batch)

    async def close(self) -> None:
        self.closed = True
        self.unsubscribe()
        for work in tuple(self.deliveries):
            work.cancel()
        await asyncio.gather(*tuple(self.deliveries), return_exceptions=True)
        # 不取消 TaskManager 内已接受的后台工作。
