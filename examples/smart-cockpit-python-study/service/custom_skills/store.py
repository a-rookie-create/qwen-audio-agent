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
            # 首次访问才从可选文件加载，之后以内存记录为准；没文件则从空目录开始。
            path = self._path(cockpit_id)
            self.records[cockpit_id] = json.loads(path.read_text()) if path and path.exists() else []
        return deepcopy(self.records[cockpit_id])  # 外部修改技能副本不会直接改动保存的定义。

    def get(self, cockpit_id: str, reference: str) -> dict | None:
        # 支持精确 ID 或忽略大小写的名称查找，供 UI 和模型工具使用。
        return next((skill for skill in self.list(cockpit_id)
                     if skill['id'] == reference or skill['name'].casefold() == reference.casefold()), None)

    def upsert(self, cockpit_id: str, definition: dict) -> dict:
        # 先校验名称及类型，未显式指定 kind 时按是否有 trigger 推断。
        name = str(definition.get('name', '')).strip()
        if not name:
            raise ValueError('技能名称不能为空')
        kind = definition.get('kind', 'event' if definition.get('trigger') else 'workflow')
        if kind not in {'workflow', 'event'}:
            raise ValueError('未知技能类型')
        existing = self.get(cockpit_id, name)
        # 同名技能沿用 ID，替换旧定义；新名称才创建新 ID。
        skill = {**deepcopy(definition), 'id': existing['id'] if existing else str(uuid4()), 'kind': kind}
        if kind == 'event':
            # 事件技能保存条件与提醒；工作流保存 instructions，二者不能混合。
            skill['trigger'] = normalize_temperature_trigger(definition.get('trigger', {}))
            if not skill.get('reminder'):
                raise ValueError('温度提醒需要提醒内容')
        elif not skill.get('instructions') or skill.get('trigger') or skill.get('reminder'):
            raise ValueError('工作流需要 instructions，不能混入温度提醒字段')
        # 校验通过后替换并按需落盘；此处只保存定义，没有执行任何工作流工具。
        self.records[cockpit_id] = [s for s in self.list(cockpit_id) if s['id'] != skill['id']] + [skill]
        self._save(cockpit_id)
        return deepcopy(skill)

    def delete(self, cockpit_id: str, reference: str) -> dict | None:
        # 找到后按 ID 删除并保存；规则刷新由外层业务 Service 负责。
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
            # 未传 root 时 path 为 None，技能仅存在内存；传入目录才写 JSON 文件。
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(self.records[cockpit_id], ensure_ascii=False, indent=2))
