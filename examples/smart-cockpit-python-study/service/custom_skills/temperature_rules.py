"""真实观察状态转换：加载规则不触发，条件外进入条件内才提醒。"""
from __future__ import annotations
import math
from uuid import uuid4
from typing import Callable
from service.state_store import CockpitStateStore


def normalize_temperature_trigger(trigger: dict) -> dict:
    value = {**trigger, 'field': trigger.get('field', 'acTemp')}
    if value.get('type') != 'vehicle_temperature' or value['field'] not in {'acTemp', 'passengerTemp', 'rearTemp'}:
        raise ValueError('不支持的温度条件')
    bounds = [value[k] for k in ('min', 'max') if k in value]
    if not bounds or any(isinstance(x, bool) or not isinstance(x, (int, float))
                         or not math.isfinite(x) or not 16 <= x <= 32 for x in bounds):
        raise ValueError('温度边界须为 16–32 的有限数值')
    if value.get('min', 16) > value.get('max', 32):
        raise ValueError('温度上下限颠倒')
    return value


class TemperatureSkillRules:
    def __init__(self, store: CockpitStateStore, list_skills: Callable, on_triggered: Callable) -> None:
        self.store, self.list_skills, self.on_triggered = store, list_skills, on_triggered
        self.entries: dict[str, dict] = {}

    def prepare(self, cockpit_id: str) -> None:
        if cockpit_id not in self.entries:
            self.entries[cockpit_id] = {'rules': [], 'previous': self.store.snapshot(cockpit_id)}
            self.store.subscribe(cockpit_id, lambda event: self.observe(cockpit_id, event))
            self.refresh(cockpit_id)

    def refresh(self, cockpit_id: str) -> None:
        entry = self.entries[cockpit_id]
        entry['rules'] = [s for s in self.list_skills(cockpit_id) if s['kind'] == 'event']
        entry['previous'] = self.store.snapshot(cockpit_id)  # 重载只建立基线。

    def observe(self, cockpit_id: str, event: dict) -> None:
        entry = self.entries[cockpit_id]
        before, after = entry['previous'], event['state']
        entry['previous'] = after
        if 'vehicle' not in event['changed']:
            return
        for skill in entry['rules']:
            trigger = skill['trigger']
            old, new = before['vehicle'][trigger['field']], after['vehicle'][trigger['field']]
            matches = lambda t: trigger.get('min', 16) <= t <= trigger.get('max', 32)
            if not matches(old) and matches(new):
                self.on_triggered({'cockpitId': cockpit_id, 'category': 'custom_skills',
                    'status': 'skill_triggered', 'eventId': str(uuid4()), 'skillId': skill['id'],
                    'skillName': skill['name'], 'message': skill['reminder'], 'trigger': trigger,
                    'temperature': new, 'previousTemperature': old, 'stateVersion': event['version']})
