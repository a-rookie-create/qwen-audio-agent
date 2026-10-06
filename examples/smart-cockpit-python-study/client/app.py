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
        self.voice = VoiceSessionController(gateway, owner_id, session_id, cockpit_id)
        self.cockpit = CockpitStateController(service, cockpit_id, self.on_activity, self.on_state)
        self.memory = GatewayMemoryController(gateway, owner_id)
        self.skills = CockpitSkillsController(service, cockpit_id)

    def start(self) -> None:
        self.voice.start()
        self.cockpit.start()

    def on_activity(self, activity: dict) -> None:
        event = skill_triggered_event(activity, self.cockpit_id)
        if event:
            self.voice.enqueue_environment(event)

    def on_state(self, state: dict) -> None:
        self.voice.enqueue_environment(navigation_preference_event(state, self.cockpit_id))

    async def send(self, text: str) -> dict:
        return await self.voice.send_text(text)

    async def wait_for_task(self, task_id: str) -> TaskRecord:
        return await self.voice.client.wait_task(task_id)

    async def close(self) -> None:
        self.cockpit.close()
        await self.voice.close()
