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
    # 由 Service 为一次工具调用构造，绑定车机 ID、共享存储及业务回调。
    cockpit_id: str
    store: CockpitStateStore
    skills: CustomSkillStore
    services: ScenarioServices
    on_skills_changed: Callable[[], None]
    on_activity: Callable[[dict], None]

    def snapshot(self) -> dict:
        # 将当前调用的 cockpit_id 固定在这里，领域执行器不必重复传递。
        return self.store.snapshot(self.cockpit_id)

    def update(self, domain: str, changes: dict) -> dict:
        # lambda 是传给 Store 的 mutate 函数：Store 取副本后调用它，合并该领域字段。
        # [domain] 告诉订阅者哪个顶层领域变化；版本增加、提交和通知由 Store 统一完成。
        return self.store.update(self.cockpit_id, [domain], lambda state: state[domain].update(changes))

    def result(self, text: str, changed: list[str] | None = None, data: dict | None = None) -> ToolResult:
        # 更新后再读最新版本并包装结果，返回文字、结构化数据和变化名单。
        return tool_result(text, self.snapshot(), changed, data)
