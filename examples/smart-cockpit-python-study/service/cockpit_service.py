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
        # 状态事件描述当前数据，activity 描述技能触发等业务过程，两个 Signal 分开。
        self.activity = Signal()
        # 传入读取技能/发布活动的方法；观察器在状态变化时调用它们，而非初始化时执行。
        self.rules = TemperatureSkillRules(self.store, self.skills.list, self.publish_activity)

    def snapshot(self, cockpit_id: str = 'default') -> dict:
        return self.store.snapshot(cockpit_id)

    def publish_activity(self, event: dict) -> None:
        # 封装业务活动并通知订阅者；发通知本身不会修改车辆或任务状态。
        self.activity.emit({'type': 'activity', **event})

    async def execute(self, name: str, args: dict, cockpit_id: str = 'default') -> ToolResult:
        self.trace.record('Service', 'execute', name)
        # 首次操作本车机时建立温度观察基线并订阅状态，之后 prepare 不会重复注册。
        self.rules.prepare(cockpit_id)
        # 给领域执行器传同一套依赖；两个 lambda 是稍后按需调用的回调函数。
        # 规则刷新回调用于技能变更，活动回调自动补上本次 cockpit_id。
        context = ToolContext(cockpit_id, self.store, self.skills, self.services,
            lambda: self.rules.refresh(cockpit_id),
            lambda event: self.publish_activity({'cockpitId': cockpit_id, **event}))
        try:
            # Registry 先查目录与参数，再分派业务执行器；它们最终通过 Store 提交状态。
            return await self.registry.execute(name, args, context)
        except (ValueError, KeyError, IndexError, TypeError) as error:
            # 将常见业务/参数错误包装成 ToolResult，让客户端和模型能看到失败原因。
            return ToolResult('操作未完成：' + str(error), state_version=self.snapshot(cockpit_id)['version'], is_error=True)

    def list_skills(self, cockpit_id: str) -> list[dict]:
        # 读取目录前确保已有规则观察器，文件加载出的事件技能也能被后续更新触发。
        self.rules.prepare(cockpit_id)
        return self.skills.list(cockpit_id)

    def delete_skill(self, cockpit_id: str, reference: str) -> dict | None:
        self.rules.prepare(cockpit_id)
        removed = self.skills.delete(cockpit_id, reference)
        # 删除定义后立即重载规则，并通知界面技能目录已变化。
        self.rules.refresh(cockpit_id)
        self.publish_activity({'cockpitId': cockpit_id, 'category': 'custom_skills', 'status': 'skills_changed'})
        return removed
