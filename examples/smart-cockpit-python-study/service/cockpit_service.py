"""HTTP 与前后台 MCP 共用此业务对象；这里拥有权威状态与技能规则。"""
from __future__ import annotations
from pathlib import Path
from service.state_store import CockpitStateStore
from service.custom_skills.store import CustomSkillStore
from service.custom_skills.temperature_rules import TemperatureSkillRules
from service.integrations.amap import ScenarioServices
from service.tools.registry import ToolRegistry
from service.tools.shared import ToolContext
from study_support import Signal, TraceLog, ToolResult


class CockpitService:
    def __init__(self, trace: TraceLog, data_dir: Path | None = None) -> None:
        self.trace = trace
        self.store = CockpitStateStore()
        self.skills = CustomSkillStore(data_dir)
        self.registry = ToolRegistry()
        self.services = ScenarioServices()
        self.activity = Signal()
        self.rules = TemperatureSkillRules(self.store, self.skills.list, self.publish_activity)

    def snapshot(self, cockpit_id: str = 'default') -> dict:
        return self.store.snapshot(cockpit_id)

    def publish_activity(self, event: dict) -> None:
        self.activity.emit({'type': 'activity', **event})

    async def execute(self, name: str, args: dict, cockpit_id: str = 'default') -> ToolResult:
        self.trace.record('Service', 'execute', name)
        self.rules.prepare(cockpit_id)
        context = ToolContext(cockpit_id, self.store, self.skills, self.services,
            lambda: self.rules.refresh(cockpit_id),
            lambda event: self.publish_activity({'cockpitId': cockpit_id, **event}))
        try:
            return await self.registry.execute(name, args, context)
        except (ValueError, KeyError, IndexError, TypeError) as error:
            return ToolResult('操作未完成：' + str(error), state_version=self.snapshot(cockpit_id)['version'], is_error=True)

    def list_skills(self, cockpit_id: str) -> list[dict]:
        self.rules.prepare(cockpit_id)
        return self.skills.list(cockpit_id)

    def delete_skill(self, cockpit_id: str, reference: str) -> dict | None:
        self.rules.prepare(cockpit_id)
        removed = self.skills.delete(cockpit_id, reference)
        self.rules.refresh(cockpit_id)
        self.publish_activity({'cockpitId': cockpit_id, 'category': 'custom_skills', 'status': 'skills_changed'})
        return removed
