"""真实的数据投影与有界环境事件队列；不执行业务命令。"""
from __future__ import annotations
import time
from collections import OrderedDict
from typing import Callable, Awaitable


def apply_cockpit_state_update(previous: dict | None, event: dict) -> dict:
    # 新建顶层字典；changed 中的领域采用事件新值，未变领域复用客户端已有对象。
    # 复用未变对象便于 UI 判断哪些部分需要刷新；version 始终采用事件里的新版本。
    current = dict(event['state'])
    if previous:
        for key in current:
            if key != 'version' and key not in event['changed'] and key in previous:
                current[key] = previous[key]
    return current


def navigation_preference_event(state: dict, cockpit_id: str) -> dict:
    # 从完整业务状态提取模型需要的导航事实，context 表示只更新上下文。
    nav = state['navigation']
    return {'name': 'cockpit.navigation.preference_changed', 'delivery_hint': 'context',
            'data': {'cockpitId': cockpit_id, 'stateVersion': state['version'],
                     'strategy': nav['strategy'], 'status': nav['status'], 'destination': nav['destination']}}


def skill_triggered_event(activity: dict, cockpit_id: str) -> dict | None:
    # 同时过滤活动类别、触发状态和车机 ID，普通技能目录变化不应变成提醒。
    if (activity.get('category'), activity.get('status'), activity.get('cockpitId')) != (
        'custom_skills', 'skill_triggered', cockpit_id):
        return None
    # 同一提醒沿用 Service 生成的 ID，队列可以据此合并同一个待发事件。
    return {'event_id': activity['eventId'], 'name': 'cockpit.skill.triggered', 'delivery_hint': 'respond',
            'data': {'reminder': activity['message'], 'trigger': activity['trigger'],
                     'temperature': activity['temperature'], 'previousTemperature': activity['previousTemperature']}}


class CockpitEnvironmentOutbox:
    def __init__(self, max_items: int = 16, ttl: float = 30, now: Callable[[], float] = time.monotonic) -> None:
        self.max_items, self.ttl, self.now = max_items, ttl, now
        # OrderedDict 保留待发顺序；context 另存每类事实的最新值，供显式恢复使用。
        self.pending: OrderedDict[str, tuple[dict, float]] = OrderedDict()
        self.context: dict[str, dict] = {}
        self.flushing = False

    def enqueue(self, event: dict) -> None:
        # 上下文按事件名合并，导航变化只保留最新事实；提醒按独立 ID 区分。
        key = event['name'] if event.get('delivery_hint') == 'context' else event['event_id']
        if event.get('delivery_hint') == 'context':
            self.context[key] = event
        self.pending[key] = (event, self.now())
        while len(self.pending) > self.max_items:
            # 队列有界，超出容量时淘汰最早排入的条目。
            self.pending.popitem(last=False)

    async def flush(self, send: Callable[[dict], Awaitable[dict]], is_ready: Callable[[], bool]) -> None:
        # 多个状态回调可能同时请求发送；flushing 保证只有一个协程在消费队列。
        if self.flushing or not is_ready():
            return
        self.flushing = True
        try:
            while self.pending and is_ready():
                key, entry = next(iter(self.pending.items()))
                event, timestamp = entry
                if event.get('delivery_hint') != 'context' and self.now() - timestamp > self.ttl:
                    # 提醒过期就丢弃；上下文事实保留到被新值覆盖，不使用提醒的 TTL。
                    self.pending.pop(key)
                    continue
                # send 是外部传入的异步函数；未获接受就保留条目，结束本次发送。
                if not (await send(event)).get('accepted'):
                    break
                # await 期间同一 key 可能被更新；只有仍是刚发送的条目才删除，保护新值。
                if self.pending.get(key) is entry:
                    self.pending.pop(key)
        finally:
            # 即使发送报错也恢复标志，后续 flush 才能再次尝试。
            self.flushing = False

    def restore_context(self) -> None:
        # 将缓存的最新事实重新排队；调用方显式调用时才会发生，本演示不自动重连。
        for event in self.context.values():
            self.enqueue(event)
