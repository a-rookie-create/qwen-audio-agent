"""状态与按钮命令直接连 Service；与 Gateway 语音通路分开。"""
from __future__ import annotations
from typing import Callable
from service.server import CockpitServiceServer
from client.projections import apply_cockpit_state_update
from study_support import ToolResult


class CockpitStateController:
    def __init__(self, server: CockpitServiceServer, cockpit_id: str, on_activity: Callable,
                 on_state: Callable) -> None:
        self.server, self.cockpit_id = server, cockpit_id
        self.on_activity, self.on_state = on_activity, on_state
        self.state: dict | None = None
        self.unsubscribe: Callable[[], None] | None = None

    def start(self) -> None:
        self.unsubscribe = self.server.subscribe(self.cockpit_id, self.handle_event)

    def handle_event(self, event: dict) -> None:
        if event['type'] == 'snapshot':
            self.state = event['state']
        elif event['type'] == 'state':
            self.state = apply_cockpit_state_update(self.state, event)
        elif event['type'] == 'activity':
            self.on_activity(event)
            return
        self.on_state(self.state)

    async def execute(self, name: str, args: dict | None = None) -> ToolResult:
        return await self.server.handle('POST', '/api/cockpit/commands',
            {'name': name, 'arguments': args or {}}, self.cockpit_id)

    def close(self) -> None:
        if self.unsubscribe:
            self.unsubscribe()
