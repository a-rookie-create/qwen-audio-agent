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
        # 保存尚未收尾的事件转发 Task，flush/close 才能等待它们。
        self.pending_events: set[asyncio.Task] = set()
        # 把 on_event 函数交给 Gateway，之后会话用它把回复和任务事件推回客户端。
        self.client = GatewayClient(gateway, owner_id, session_id, cockpit_id, self.on_event)

    def start(self) -> None:
        self.client.start()

    def on_event(self, event: dict) -> None:
        # 保留全部事件用于观察调用链，只有 reply 事件进入展示用的消息列表。
        self.events.append(event)
        if event['type'] == 'reply':
            self.messages.append(event)
            if self.on_message:
                self.on_message(event)
            if event.get('task_id') and self.auto_play:
                # 收到后台回复后确认播放，任务通知才从 delivering 变成 delivered。
                self.client.playback_ack(event['task_id'])  # 本地“播放完成”模拟，不是扬声器播放。

    async def send_text(self, text: str) -> dict:
        return await self.client.send({'type': 'input.message', 'text': text})

    async def send_audio(self, audio: bytes) -> dict:
        # 本学习版传入的是 UTF-8 文本字节，服务端解码后走与文字输入相同的路径。
        return await self.client.send({'type': 'audio.append', 'audio': audio})

    def enqueue_environment(self, event: dict) -> None:
        self.environment.enqueue(event)
        # 状态观察回调是同步函数，不能直接 await；创建 Task 交给事件循环稍后处理。
        work = asyncio.create_task(self.flush_environment())
        self.pending_events.add(work)
        # 传入 discard 函数，而非现在调用；Task 结束后会用自身作为参数执行它。
        work.add_done_callback(self.pending_events.discard)

    async def flush_environment(self) -> None:
        # 两个 lambda 都是函数参数：一个发送事件，一个在发送前检查会话是否可用。
        # 静音时保留队列，取消静音后再尝试发送。
        await self.environment.flush(lambda event: self.client.request('client.event.publish', event),
                                      lambda: self.client.session is not None and not self.client.session.muted)

    async def flush(self) -> None:
        # 取集合快照等本批 Task，循环处理等待期间新增的 Task。
        while self.pending_events:
            batch = tuple(self.pending_events)
            await asyncio.gather(*batch)
            # 主动清理已等待的这一批，避免只依赖稍后执行的 done 回调。
            self.pending_events.difference_update(batch)

    async def select_persona(self, profile_id: str) -> dict:
        # 人设通过客户端事件修改当前会话模型的配置，不修改车机业务状态。
        return await self.client.request('client.event.publish', {
            'name': 'cockpit.assistant_profile.selected', 'data': {'profile': profile_id}})

    async def mute(self, muted: bool) -> None:
        await self.client.send({'type': 'mute' if muted else 'unmute'})
        if not muted:
            # 会话内待播的后台结果由 unmute 分支唤醒；这里另外发送积压的环境事件。
            await self.flush_environment()

    async def close(self) -> None:
        # 等已创建的转发任务收尾，再停止会话；Gateway 的后台工作由运行时单独管理。
        await self.flush()
        await self.client.stop()
