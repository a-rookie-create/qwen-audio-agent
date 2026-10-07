"""可运行的客户端：连接输入、状态、技能、记忆和环境提醒。"""
from __future__ import annotations
from framework_reference.gateway_application import GatewayApplication
from framework_reference.task_runtime import TaskRecord
from service.server import CockpitServiceServer
from client.voice_session import VoiceSessionController
from client.cockpit_state import CockpitStateController
from client.memory_and_skills import GatewayMemoryController, CockpitSkillsController
from client.projections import skill_triggered_event, navigation_preference_event


class CockpitApp:
    def __init__(self, gateway: GatewayApplication, service: CockpitServiceServer,
                 owner_id: str = 'demo-user', session_id: str = 'main', cockpit_id: str = 'default') -> None:
        self.cockpit_id = cockpit_id
        # 语音/文字通路连接 Gateway；业务状态与按钮命令直接连接 Service。
        self.voice = VoiceSessionController(gateway, owner_id, session_id, cockpit_id)
        # 传入两个方法作为回调，收到状态/活动事件时才由控制器调用。
        self.cockpit = CockpitStateController(service, cockpit_id, self.on_activity, self.on_state)
        self.memory = GatewayMemoryController(gateway, owner_id)
        self.skills = CockpitSkillsController(service, cockpit_id)

    def start(self) -> None:
        # 先连会话，再订阅状态。订阅立即推送的快照会产生待发往会话的环境事件。
        self.voice.start()
        self.cockpit.start()

    def on_activity(self, activity: dict) -> None:
        # 仅把本车机的技能触发活动转换为提醒事件，其他业务活动不会进入对话。
        event = skill_triggered_event(activity, self.cockpit_id)
        if event:
            self.voice.enqueue_environment(event)

    def on_state(self, state: dict) -> None:
        # 从业务状态提取导航事实供模型参考；这条事件只更新上下文，不直接播报。
        self.voice.enqueue_environment(navigation_preference_event(state, self.cockpit_id))

    async def send(self, text: str) -> dict:
        return await self.voice.send_text(text)

    async def wait_for_task(self, task_id: str) -> TaskRecord:
        # 等待任务执行与当前会话的投递处理，不创建新任务，也不再执行工具。
        return await self.voice.client.wait_task(task_id)

    async def close(self) -> None:
        # 先断开状态订阅，防止关闭会话时又收到事件并创建新的转发任务。
        self.cockpit.close()
        await self.voice.close()
