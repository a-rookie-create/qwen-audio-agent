"""真正的后台任务与通知：状态归 TaskManager，前台会话只观察并展示。"""
from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from typing import Callable, Awaitable, TYPE_CHECKING
from uuid import uuid4
from study_support import Signal, ToolResult, TraceLog
from framework_reference.backend_adapter import BackendWorkRuntime
# 仅供类型检查器读取，运行时不导入会话模块，避免任务模块与会话模块循环导入。
if TYPE_CHECKING:
    from framework_reference.frontend_session import RealtimeSessionRuntime


@dataclass
class TaskRecord:
    id: str
    objective: str
    owner_id: str
    session_id: str
    status: str = 'queued'
    # status 记录执行阶段；notification 独立记录结果是否已发送、是否确认播放。
    notification: str = 'none'
    result: ToolResult | None = None
    work: asyncio.Task | None = None
    # 每个任务有自己的完成事件；wait 等此事件，而不是反复轮询 status。
    finished: asyncio.Event = field(default_factory=asyncio.Event)

    def snapshot(self) -> dict:
        # 只暴露展示用字段，不把内部 Task/Event 或可变的 TaskRecord 交给客户端。
        return {'id': self.id, 'objective': self.objective, 'ownerId': self.owner_id,
                'sessionId': self.session_id, 'status': self.status,
                'notification': self.notification,
                'result': self.result.content if self.result else None}


class TaskManager:
    def __init__(self, trace: TraceLog) -> None:
        self.trace = trace
        self.tasks: dict[str, TaskRecord] = {}
        self.events = Signal()
        # 按用户保存锁：同一用户的后台操作排队，不同用户可以在等待期间交错推进。
        self.owner_locks: dict[str, asyncio.Lock] = {}

    def create(self, objective: str, owner_id: str, session_id: str,
               runner: Callable[[TaskRecord], Awaitable[ToolResult]]) -> TaskRecord:
        task = TaskRecord(uuid4().hex, objective, owner_id, session_id)
        self.tasks[task.id] = task
        self.emit('task.accepted', task)
        # create_task 安排稍后执行协程；这里不 await，所以前台立即拿到 queued 记录。
        task.work = asyncio.create_task(self._execute(task, runner))
        return task  # 创建记录后就返回，不等待模型工具循环。

    async def _execute(self, task: TaskRecord, runner: Callable) -> None:
        try:
            lock = self.owner_locks.setdefault(task.owner_id, asyncio.Lock())
            async with lock:  # 同一个用户的后台工作依次运行。
                # 只有拿到锁才进入 running，等待锁期间仍是 queued。
                task.status = 'running'
                self.emit('task.running', task)
                # runner 是提交时传入的异步执行函数，最终会调用后台 Agent。
                result = await runner(task)
                self._finish(task, 'completed', result)
        except asyncio.CancelledError:
            # 取消结束后续执行，但先前工具已保存的业务状态不会自动回滚。
            self._finish(task, 'cancelled', ToolResult('已取消，已执行操作不会自动回滚。'))
        except Exception as error:
            self._finish(task, 'failed', ToolResult(str(error), is_error=True))

    def _finish(self, task: TaskRecord, status: str, result: ToolResult) -> None:
        # 先保存执行结果，再发事实事件；完成执行和把结果通知用户是两个阶段。
        task.status, task.result = status, result
        self.emit('task.' + status, task)
        if status in {'completed', 'failed'}:
            # 成功和失败都需要向会话报告；取消任务在这里不安排结果播报。
            task.notification = 'pending'
            self.emit('task.notification.pending', task)
        task.finished.set()  # 唤醒所有等执行完成的协程，不代表结果已经播放。

    def emit(self, event_type: str, task: TaskRecord, message: str = '') -> None:
        self.trace.record('TaskManager', event_type, task.id)
        self.events.emit({'type': event_type, 'task': task.snapshot(), 'message': message})

    def get(self, task_id: str, owner_id: str) -> TaskRecord:
        # 所有读取、等待、取消、播放确认共用此检查，按 owner_id 隔离任务。
        task = self.tasks[task_id]
        if task.owner_id != owner_id:
            raise PermissionError('不能读取其他用户的任务')
        return task

    async def wait(self, task_id: str, owner_id: str) -> TaskRecord:
        task = self.get(task_id, owner_id)
        # await 期间让出事件循环，前台请求和其他 Task 仍能被处理。
        await task.finished.wait()
        return task

    async def cancel(self, task_id: str, owner_id: str) -> None:
        task = self.get(task_id, owner_id)
        if task.status in {'completed', 'failed', 'cancelled'}:
            return
        if task.work:
            # cancel 发出取消请求；gather 等待协程处理取消并执行它的收尾逻辑。
            task.work.cancel()
            await asyncio.gather(task.work, return_exceptions=True)
        if not task.finished.is_set():  # 处理协程尚未开始就被取消的情形。
            self._finish(task, 'cancelled', ToolResult('排队任务已取消'))

    def mark_delivered(self, task_id: str, owner_id: str) -> None:
        task = self.get(task_id, owner_id)
        # 只有已开始投递的结果可确认；重复确认不会再次改变通知状态。
        if task.notification == 'delivering':
            task.notification = 'delivered'
            self.emit('task.notification.delivered', task)

    async def close(self) -> None:
        # 关闭整个 Gateway 时清理所有未结束任务；关闭单个会话不会走到这里。
        for task in tuple(self.tasks.values()):
            await self.cancel(task.id, task.owner_id)


class TaskOperations:
    def __init__(self, tasks: TaskManager, backend: BackendWorkRuntime) -> None:
        self.tasks, self.backend = tasks, backend

    def submit(self, objective: str, owner_id: str, session_id: str) -> TaskRecord:
        # 内部 runner 记住当前 TaskRecord，把 Agent 的进度回调转换为任务事件。
        # 定义 runner 不会执行它，TaskManager 拿到用户锁后才调用。
        async def runner(task: TaskRecord) -> ToolResult:
            return await self.backend.run(task, lambda message: self.tasks.emit('task.progress', task, message))
        return self.tasks.create(objective, owner_id, session_id, runner)

    async def cancel(self, task_id: str, owner_id: str) -> None:
        # 先校验归属，再通知 Agent 和 TaskManager 两层停止，避免越权取消。
        self.tasks.get(task_id, owner_id)
        self.backend.cancel(task_id)
        await self.tasks.cancel(task_id, owner_id)


class SessionTaskCoordinator:
    def __init__(self, tasks: TaskManager, session: RealtimeSessionRuntime) -> None:
        self.tasks, self.session = tasks, session
        self.pending: set[str] = set()
        # pending 保存待通知的任务 ID；deliveries 保存正在执行的投递协程。
        self.deliveries: set[asyncio.Task] = set()
        self.closed = False
        # 保存取消订阅函数，会话关闭时调用；这里并未立即取消订阅。
        self.unsubscribe = tasks.events.subscribe(self.on_event)

    def on_event(self, event: dict) -> None:
        snapshot = event['task']
        # 共享 TaskManager 发出所有任务事件，此会话只接收当前用户且当前会话的事件。
        if (snapshot['ownerId'], snapshot['sessionId']) != (self.session.owner_id, self.session.session_id):
            return
        self.session.send(event)  # 任务进度与聊天回复都是客户端可观察事件。
        if event['type'] == 'task.notification.pending':
            self.pending.add(snapshot['id'])
            self.refresh()

    def refresh(self) -> None:
        # 静音/关闭时保留 pending，不启动播报；取消静音会再次调用 refresh。
        if self.closed or not self.session.can_announce():
            return
        for task_id in tuple(self.pending):
            task = self.tasks.get(task_id, self.session.owner_id)
            if task.notification == 'pending':
                # 创建投递 Task 之前先改状态，避免多次 refresh 重复安排同一个结果。
                task.notification = 'delivering'
                work = asyncio.create_task(self._deliver(task))
                self.deliveries.add(work)
                # 回调在 work 完成后调用 discard(work)，从正在投递的集合中移除它。
                work.add_done_callback(self.deliveries.discard)

    async def _deliver(self, task: TaskRecord) -> None:
        # present 负责把回复送到客户端；播放回执另由 mark_delivered 修改通知状态。
        delivered = await self.session.present_task_result(task)
        if not delivered:
            # 创建投递 Task 后会话可能已变成不可播报，退回 pending 供以后再尝试。
            task.notification = 'pending'
        if task.notification == 'delivered':
            self.pending.discard(task.id)

    async def flush(self) -> None:
        # 等待当前可投递的结果处理完；静音结果仍保留 pending，不在这里强行播报。
        self.refresh()
        while self.deliveries:
            batch = tuple(self.deliveries)
            await asyncio.gather(*batch)
            # 已完成 future 的 gather 可能不让出事件循环；不能只等 done 回调清理集合。
            self.deliveries.difference_update(batch)

    async def close(self) -> None:
        self.closed = True
        # 停止接收新的任务事件，并取消本会话投递；已接受的后台任务属于 TaskManager。
        self.unsubscribe()
        for work in tuple(self.deliveries):
            work.cancel()
        await asyncio.gather(*tuple(self.deliveries), return_exceptions=True)
        # 不取消 TaskManager 内已接受的后台工作。
