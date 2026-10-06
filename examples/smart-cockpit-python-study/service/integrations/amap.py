"""可替换的外部业务适配；本学习版使用明确标记的离线演示数据。"""
from __future__ import annotations
from typing import Any


class ScenarioServices:
    def weather(self, city: str) -> dict[str, Any]:
        return {'city': city, 'temperature': 24, 'condition': '晴（演示）', 'source': 'offline-demo'}

    def resolve_place(self, name: str) -> dict[str, str]:
        if not name.strip():
            raise ValueError('地点不能为空')
        return {'name': name, 'source': 'offline-demo'}

    def plan_route(self, origin: str, destination: str, waypoints: list[str], strategy: int) -> dict:
        self.resolve_place(destination)
        for waypoint in waypoints:
            self.resolve_place(waypoint)
        return {'origin': origin, 'destination': destination, 'waypoints': list(waypoints),
                'strategy': strategy, 'distanceKm': 10 + 3 * len(waypoints),
                'minutes': 20 + 5 * len(waypoints), 'source': 'offline-demo'}

    def search_places(self, query: str) -> list[dict[str, str]]:
        return [self.resolve_place(query or '附近停车场')]

    def vehicle_location(self) -> dict[str, str]:
        return {'address': '演示车位', 'source': 'offline-demo'}
