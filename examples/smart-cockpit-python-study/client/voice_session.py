"""实际客户端控制器：发送输入、接收回复、模拟播放确认与场景事件。"""
from __future__ import annotations
import asyncio
from typing import Callable
from framework_reference.gateway_application import GatewayApplication
from framework_reference.gateway_client import GatewayClient
from client.projections import CockpitEnvironmentOutbox


class VoiceSessionController:
    def __init__(self, gateway: GatewayApplication, owner_id: str, session_id: str, cockpit_id: str) -> None:
        self.messages: list[dict] = []
        self.events: list[dict] = []
        self.auto_play = True
        self.on_message: Callable[[dict], None] | None = None
        self.environment = CockpitEnvironmentOutbox()
        self.pending_events: set[asyncio.Task] = set()
        self.client = GatewayClient(gateway, owner_id, session_id, cockpit_id, self.on_event)

    def start(self) -> None:
        self.client.start()

    def on_event(self, event: dict) -> None:
        self.events.append(event)
        if event['type'] == 'reply':
            self.messages.append(event)
            if self.on_message:
                self.on_message(event)
            if event.get('task_id') and self.auto_play:
                self.client.playback_ack(event['task_id'])  # 本地“播放完成”模拟，不是扬声器播放。

    async def send_text(self, text: str) -> dict:
        return await self.client.send({'type': 'input.message', 'text': text})

    async def send_audio(self, audio: bytes) -> dict:
        return await self.client.send({'type': 'audio.append', 'audio': audio})

    def enqueue_environment(self, event: dict) -> None:
        self.environment.enqueue(event)
        work = asyncio.create_task(self.flush_environment())
        self.pending_events.add(work)
        work.add_done_callback(self.pending_events.discard)

    async def flush_environment(self) -> None:
        await self.environment.flush(lambda event: self.client.request('client.event.publish', event),
                                      lambda: self.client.session is not None and not self.client.session.muted)

    async def flush(self) -> None:
        while self.pending_events:
            batch = tuple(self.pending_events)
            await asyncio.gather(*batch)
            self.pending_events.difference_update(batch)

    async def select_persona(self, profile_id: str) -> dict:
        return await self.client.request('client.event.publish', {
            'name': 'cockpit.assistant_profile.selected', 'data': {'profile': profile_id}})

    async def mute(self, muted: bool) -> None:
        await self.client.send({'type': 'mute' if muted else 'unmute'})
        if not muted:
            await self.flush_environment()

    async def close(self) -> None:
        await self.flush()
        await self.client.stop()
