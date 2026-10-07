"""进程内 HTTP/SSE 边界模拟；每个客户端拿到同一 Service 的状态事件。"""
from __future__ import annotations
from typing import Callable
from service.cockpit_service import CockpitService
from service.mcp_server import CockpitMcpServer


class CockpitServiceServer:
    def __init__(self, service: CockpitService) -> None:
        self.service = service

    def mcp(self, surface: str, cockpit_id: str = 'default') -> CockpitMcpServer:
        # 两个工具面绑定同一个业务 Service，只是暴露的工具目录不同。
        if surface not in {'frontend', 'backend'}:
            raise ValueError('未知 MCP 面')
        return CockpitMcpServer(self.service, surface, cockpit_id)

    async def handle(self, method: str, path: str, body: dict | None = None,
                     cockpit_id: str = 'default'):
        # 用 method + path 模拟 HTTP 路由；各入口仍委托给同一个业务对象。
        body = body or {}
        if (method, path) == ('GET', '/health'):
            return {'ok': True}
        if (method, path) == ('GET', '/api/cockpit/state'):
            return self.service.snapshot(cockpit_id)
        if (method, path) == ('POST', '/api/cockpit/commands'):
            # UI 命令也走 execute 的校验和状态更新，不单独维护一份面板数据。
            return await self.service.execute(body['name'], body.get('arguments', {}), cockpit_id)
        if (method, path) == ('POST', '/api/cockpit/reset'):
            return self.service.store.reset(cockpit_id)
        if (method, path) == ('GET', '/api/cockpit/skills'):
            return self.service.list_skills(cockpit_id)
        if path.startswith('/api/cockpit/skills/'):
            # 路径末段作为技能 ID 或名称；删除经业务层刷新规则，读取只取定义。
            reference = path.rsplit('/', 1)[-1]
            if method == 'GET':
                return self.service.skills.get(cockpit_id, reference)
            if method == 'DELETE':
                return self.service.delete_skill(cockpit_id, reference)
        raise ValueError('未知接口：' + method + ' ' + path)

    def subscribe(self, cockpit_id: str, listener: Callable) -> Callable[[], None]:
        # 先立即调用 listener 给出初始快照，客户端不用等第一次变化才能显示状态。
        listener({'type': 'snapshot', 'state': self.service.snapshot(cockpit_id)})
        unsubscribe_state = self.service.store.subscribe(cockpit_id, listener)
        # 状态和活动两条订阅共用客户端回调；活动额外按车机 ID 过滤。
        def on_activity(event: dict) -> None:
            if event['cockpitId'] == cockpit_id:
                listener(event)
        unsubscribe_activity = self.service.activity.subscribe(on_activity)
        # 返回一个合并的取消函数；只有调用它时，下面两次取消才真正执行。
        def unsubscribe() -> None:
            unsubscribe_state()
            unsubscribe_activity()
        return unsubscribe
