"""客户端 SDK 的进程内实现；方法真正调用 Gateway/会话，支持 IDE 跳转。"""
from __future__ import annotations
from typing import Callable
from framework_reference.gateway_application import GatewayApplication
from framework_reference.frontend_session import RealtimeSessionRuntime
from framework_reference.task_runtime import TaskRecord


class GatewayClient:
    def __init__(self, gateway: GatewayApplication, owner_id: str, session_id: str,
                 cockpit_id: str, on_event: Callable[[dict], None]) -> None:
        self.gateway, self.owner_id, self.session_id = gateway, owner_id, session_id
        self.cockpit_id, self.on_event = cockpit_id, on_event
        self.session: RealtimeSessionRuntime | None = None

    def start(self) -> None:
        self.session = self.gateway.connect(self.owner_id, self.session_id, self.on_event, self.cockpit_id)

    async def send(self, event: dict) -> dict:
        if not self.session:
            raise RuntimeError('客户端尚未连接')
        return await self.session.handle_client_event(event)

    async def request(self, name: str, payload: dict) -> dict:
        if name == 'task.create':
            return self.gateway.operations.submit(payload['objective'], self.owner_id, self.session_id).snapshot()
        if name == 'task.cancel':
            await self.gateway.operations.cancel(payload['task_id'], self.owner_id)
            return {'accepted': True}
        if name == 'task.get':
            return self.gateway.tasks.get(payload['task_id'], self.owner_id).snapshot()
        return await self.send({'type': name, **payload})

    async def wait_task(self, task_id: str) -> TaskRecord:
        task = await self.gateway.tasks.wait(task_id, self.owner_id)
        if self.session and self.session.coordinator:
            await self.session.coordinator.flush()
        return task

    def playback_ack(self, task_id: str) -> None:
        self.gateway.tasks.mark_delivered(task_id, self.owner_id)

    async def stop(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
