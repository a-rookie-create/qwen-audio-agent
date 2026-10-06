"""真实的数据投影与有界环境事件队列；不执行业务命令。"""
from __future__ import annotations
import time
from collections import OrderedDict
from typing import Callable, Awaitable


def apply_cockpit_state_update(previous: dict | None, event: dict) -> dict:
    current = dict(event['state'])
    if previous:
        for key in current:
            if key != 'version' and key not in event['changed'] and key in previous:
                current[key] = previous[key]
    return current


def navigation_preference_event(state: dict, cockpit_id: str) -> dict:
    nav = state['navigation']
    return {'name': 'cockpit.navigation.preference_changed', 'delivery_hint': 'context',
            'data': {'cockpitId': cockpit_id, 'stateVersion': state['version'],
                     'strategy': nav['strategy'], 'status': nav['status'], 'destination': nav['destination']}}


def skill_triggered_event(activity: dict, cockpit_id: str) -> dict | None:
    if (activity.get('category'), activity.get('status'), activity.get('cockpitId')) != (
        'custom_skills', 'skill_triggered', cockpit_id):
        return None
    return {'event_id': activity['eventId'], 'name': 'cockpit.skill.triggered', 'delivery_hint': 'respond',
            'data': {'reminder': activity['message'], 'trigger': activity['trigger'],
                     'temperature': activity['temperature'], 'previousTemperature': activity['previousTemperature']}}


class CockpitEnvironmentOutbox:
    def __init__(self, max_items: int = 16, ttl: float = 30, now: Callable[[], float] = time.monotonic) -> None:
        self.max_items, self.ttl, self.now = max_items, ttl, now
        self.pending: OrderedDict[str, tuple[dict, float]] = OrderedDict()
        self.context: dict[str, dict] = {}
        self.flushing = False

    def enqueue(self, event: dict) -> None:
        key = event['name'] if event.get('delivery_hint') == 'context' else event['event_id']
        if event.get('delivery_hint') == 'context':
            self.context[key] = event
        self.pending[key] = (event, self.now())
        while len(self.pending) > self.max_items:
            self.pending.popitem(last=False)

    async def flush(self, send: Callable[[dict], Awaitable[dict]], is_ready: Callable[[], bool]) -> None:
        if self.flushing or not is_ready():
            return
        self.flushing = True
        try:
            while self.pending and is_ready():
                key, entry = next(iter(self.pending.items()))
                event, timestamp = entry
                if event.get('delivery_hint') != 'context' and self.now() - timestamp > self.ttl:
                    self.pending.pop(key)
                    continue
                if not (await send(event)).get('accepted'):
                    break
                if self.pending.get(key) is entry:
                    self.pending.pop(key)
        finally:
            self.flushing = False

    def restore_context(self) -> None:
        for event in self.context.values():
            self.enqueue(event)
