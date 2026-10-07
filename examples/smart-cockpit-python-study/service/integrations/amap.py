"""可替换的外部业务适配；本学习版使用明确标记的离线演示数据。"""
from __future__ import annotations
from typing import Any


class ScenarioServices:
    # 将外部数据能力集中在一个可替换对象，业务工具无需自己请求地图/天气供应商。
    def weather(self, city: str) -> dict[str, Any]:
        return {'city': city, 'temperature': 24, 'condition': '晴（演示）', 'source': 'offline-demo'}

    def resolve_place(self, name: str) -> dict[str, str]:
        # 本版只检查名称非空并标记来源，没有真实地理编码。
        if not name.strip():
            raise ValueError('地点不能为空')
        return {'name': name, 'source': 'offline-demo'}

    def plan_route(self, origin: str, destination: str, waypoints: list[str], strategy: int) -> dict:
        # 先验证目的地和全部途经点，再生成按途经点数量计算的演示距离与时长。
        self.resolve_place(destination)
        for waypoint in waypoints:
            self.resolve_place(waypoint)
        return {'origin': origin, 'destination': destination, 'waypoints': list(waypoints),
                'strategy': strategy, 'distanceKm': 10 + 3 * len(waypoints),
                'minutes': 20 + 5 * len(waypoints), 'source': 'offline-demo'}

    def search_places(self, query: str) -> list[dict[str, str]]:
        # 空查询使用固定演示地点，返回与导航工具约定的地点列表格式。
        return [self.resolve_place(query or '附近停车场')]

    def vehicle_location(self) -> dict[str, str]:
        return {'address': '演示车位', 'source': 'offline-demo'}
