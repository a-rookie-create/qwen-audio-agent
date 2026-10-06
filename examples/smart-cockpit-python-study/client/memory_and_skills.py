"""两组真实方法调用：记忆归 Gateway，技能归 Service。"""
from framework_reference.gateway_application import GatewayApplication
from service.server import CockpitServiceServer


class GatewayMemoryController:
    def __init__(self, gateway: GatewayApplication, owner_id: str) -> None:
        self.gateway, self.owner_id = gateway, owner_id

    async def load(self) -> list[dict]:
        return (await self.gateway.memory_request(self.owner_id, 'GET'))['documents']

    async def remove(self, item: dict) -> list[dict]:
        return (await self.gateway.memory_request(self.owner_id, 'PATCH', {'changes': [
            {'operation': 'remove', 'id': item['id'], 'version': item['version']}]}))['documents']


class CockpitSkillsController:
    def __init__(self, server: CockpitServiceServer, cockpit_id: str) -> None:
        self.server, self.cockpit_id = server, cockpit_id

    async def list(self) -> list[dict]:
        return await self.server.handle('GET', '/api/cockpit/skills', cockpit_id=self.cockpit_id)

    async def load(self, skill_id: str) -> dict | None:
        return await self.server.handle('GET', '/api/cockpit/skills/' + skill_id, cockpit_id=self.cockpit_id)

    async def remove(self, skill_id: str) -> dict | None:
        return await self.server.handle('DELETE', '/api/cockpit/skills/' + skill_id, cockpit_id=self.cockpit_id)
