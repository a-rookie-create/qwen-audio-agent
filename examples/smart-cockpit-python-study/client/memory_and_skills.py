"""两组真实方法调用：记忆归 Gateway，技能归 Service。"""
from framework_reference.gateway_application import GatewayApplication
from service.server import CockpitServiceServer


class GatewayMemoryController:
    def __init__(self, gateway: GatewayApplication, owner_id: str) -> None:
        self.gateway, self.owner_id = gateway, owner_id

    async def load(self) -> list[dict]:
        # owner_id 限定用户范围，读取 Gateway 保存的长期记忆。
        return (await self.gateway.memory_request(self.owner_id, 'GET'))['documents']

    async def remove(self, item: dict) -> list[dict]:
        # 删除携带读取时的版本，Provider 会检查是否仍是同一版，冲突时要求刷新。
        return (await self.gateway.memory_request(self.owner_id, 'PATCH', {'changes': [
            {'operation': 'remove', 'id': item['id'], 'version': item['version']}]}))['documents']


class CockpitSkillsController:
    # 技能属于车机业务数据，使用 cockpit_id 访问 Service，而非 Gateway 的记忆接口。
    def __init__(self, server: CockpitServiceServer, cockpit_id: str) -> None:
        self.server, self.cockpit_id = server, cockpit_id

    async def list(self) -> list[dict]:
        return await self.server.handle('GET', '/api/cockpit/skills', cockpit_id=self.cockpit_id)

    async def load(self, skill_id: str) -> dict | None:
        # 这里只读取技能定义；运行工作流需要前台把 instructions 转为已有工具调用。
        return await self.server.handle('GET', '/api/cockpit/skills/' + skill_id, cockpit_id=self.cockpit_id)

    async def remove(self, skill_id: str) -> dict | None:
        # Service 删除后会刷新温度规则，避免已删除的事件技能继续触发提醒。
        return await self.server.handle('DELETE', '/api/cockpit/skills/' + skill_id, cockpit_id=self.cockpit_id)
