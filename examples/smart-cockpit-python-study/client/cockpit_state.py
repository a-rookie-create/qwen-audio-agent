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
        # state 是客户端显示用的副本；业务权威数据仍保存在 Service 的 Store。
        self.state: dict | None = None
        self.unsubscribe: Callable[[], None] | None = None

    def start(self) -> None:
        # subscribe 会先同步调用 handle_event 给出快照，再返回取消订阅函数。
        self.unsubscribe = self.server.subscribe(self.cockpit_id, self.handle_event)

    def handle_event(self, event: dict) -> None:
        # 初次连接直接采用完整快照；后续状态事件按 changed 合并更新。
        if event['type'] == 'snapshot':
            self.state = event['state']
        elif event['type'] == 'state':
            self.state = apply_cockpit_state_update(self.state, event)
        elif event['type'] == 'activity':
            # 活动消息交给另一条回调处理；return 避免把它当成状态再转发一次。
            self.on_activity(event)
            return
        self.on_state(self.state)  # 调用 App 的状态回调，让新的导航事实进入事件队列。

    async def execute(self, name: str, args: dict | None = None) -> ToolResult:
        # 模拟 UI 按钮请求，最终仍走与模型工具相同的 Service.execute。
        return await self.server.handle('POST', '/api/cockpit/commands',
            {'name': name, 'arguments': args or {}}, self.cockpit_id)

    def close(self) -> None:
        if self.unsubscribe:
            # 此处才执行 start 时保存的取消函数，一次取消状态和活动两条订阅。
            self.unsubscribe()
