"""进程内 HTTP/SSE 边界模拟；每个客户端拿到同一 Service 的状态事件。"""
from __future__ import annotations
from typing import Callable
from service.cockpit_service import CockpitService
from service.mcp_server import CockpitMcpServer


class CockpitServiceServer:
    def __init__(self, service: CockpitService) -> None:
        self.service = service

    def mcp(self, surface: str, cockpit_id: str = 'default') -> CockpitMcpServer:
        if surface not in {'frontend', 'backend'}:
            raise ValueError('未知 MCP 面')
        return CockpitMcpServer(self.service, surface, cockpit_id)

    async def handle(self, method: str, path: str, body: dict | None = None,
                     cockpit_id: str = 'default'):
        body = body or {}
        if (method, path) == ('GET', '/health'):
            return {'ok': True}
        if (method, path) == ('GET', '/api/cockpit/state'):
            return self.service.snapshot(cockpit_id)
        if (method, path) == ('POST', '/api/cockpit/commands'):
            return await self.service.execute(body['name'], body.get('arguments', {}), cockpit_id)
        if (method, path) == ('POST', '/api/cockpit/reset'):
            return self.service.store.reset(cockpit_id)
        if (method, path) == ('GET', '/api/cockpit/skills'):
            return self.service.list_skills(cockpit_id)
        if path.startswith('/api/cockpit/skills/'):
            reference = path.rsplit('/', 1)[-1]
            if method == 'GET':
                return self.service.skills.get(cockpit_id, reference)
            if method == 'DELETE':
                return self.service.delete_skill(cockpit_id, reference)
        raise ValueError('未知接口：' + method + ' ' + path)

    def subscribe(self, cockpit_id: str, listener: Callable) -> Callable[[], None]:
        listener({'type': 'snapshot', 'state': self.service.snapshot(cockpit_id)})
        unsubscribe_state = self.service.store.subscribe(cockpit_id, listener)
        def on_activity(event: dict) -> None:
            if event['cockpitId'] == cockpit_id:
                listener(event)
        unsubscribe_activity = self.service.activity.subscribe(on_activity)
        def unsubscribe() -> None:
            unsubscribe_state()
            unsubscribe_activity()
        return unsubscribe
