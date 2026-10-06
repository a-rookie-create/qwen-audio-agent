"""领域工具共用的执行上下文，让 IDE 能直接跳到业务依赖。"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from service.state_store import CockpitStateStore
from service.custom_skills.store import CustomSkillStore
from service.integrations.amap import ScenarioServices
from study_support import ToolResult, tool_result


@dataclass
class ToolContext:
    cockpit_id: str
    store: CockpitStateStore
    skills: CustomSkillStore
    services: ScenarioServices
    on_skills_changed: Callable[[], None]
    on_activity: Callable[[dict], None]

    def snapshot(self) -> dict:
        return self.store.snapshot(self.cockpit_id)

    def update(self, domain: str, changes: dict) -> dict:
        return self.store.update(self.cockpit_id, [domain], lambda state: state[domain].update(changes))

    def result(self, text: str, changed: list[str] | None = None, data: dict | None = None) -> ToolResult:
        return tool_result(text, self.snapshot(), changed, data)
