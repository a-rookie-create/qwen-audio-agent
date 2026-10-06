"""固定工具管理技能定义；可选择文件持久化，创建不执行工作流。"""
from __future__ import annotations
import json
from pathlib import Path
from uuid import uuid4
from copy import deepcopy
from service.custom_skills.temperature_rules import normalize_temperature_trigger


class CustomSkillStore:
    def __init__(self, root: Path | None = None) -> None:
        self.root = root
        self.records: dict[str, list[dict]] = {}

    def list(self, cockpit_id: str = 'default') -> list[dict]:
        if cockpit_id not in self.records:
            path = self._path(cockpit_id)
            self.records[cockpit_id] = json.loads(path.read_text()) if path and path.exists() else []
        return deepcopy(self.records[cockpit_id])

    def get(self, cockpit_id: str, reference: str) -> dict | None:
        return next((skill for skill in self.list(cockpit_id)
                     if skill['id'] == reference or skill['name'].casefold() == reference.casefold()), None)

    def upsert(self, cockpit_id: str, definition: dict) -> dict:
        name = str(definition.get('name', '')).strip()
        if not name:
            raise ValueError('技能名称不能为空')
        kind = definition.get('kind', 'event' if definition.get('trigger') else 'workflow')
        if kind not in {'workflow', 'event'}:
            raise ValueError('未知技能类型')
        existing = self.get(cockpit_id, name)
        skill = {**deepcopy(definition), 'id': existing['id'] if existing else str(uuid4()), 'kind': kind}
        if kind == 'event':
            skill['trigger'] = normalize_temperature_trigger(definition.get('trigger', {}))
            if not skill.get('reminder'):
                raise ValueError('温度提醒需要提醒内容')
        elif not skill.get('instructions') or skill.get('trigger') or skill.get('reminder'):
            raise ValueError('工作流需要 instructions，不能混入温度提醒字段')
        self.records[cockpit_id] = [s for s in self.list(cockpit_id) if s['id'] != skill['id']] + [skill]
        self._save(cockpit_id)
        return deepcopy(skill)

    def delete(self, cockpit_id: str, reference: str) -> dict | None:
        skill = self.get(cockpit_id, reference)
        if skill:
            self.records[cockpit_id] = [s for s in self.list(cockpit_id) if s['id'] != skill['id']]
            self._save(cockpit_id)
        return skill

    def _path(self, cockpit_id: str) -> Path | None:
        # 编码 ID 形成文件名，避免把用户 ID 当文件路径。
        return self.root / (cockpit_id.encode().hex() + '.json') if self.root else None

    def _save(self, cockpit_id: str) -> None:
        path = self._path(cockpit_id)
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.records[cockpit_id], ensure_ascii=False, indent=2))
