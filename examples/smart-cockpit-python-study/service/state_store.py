"""业务状态的唯一来源；同一个更新事件同时驱动 UI 和规则观察器。"""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Callable
from study_support import Signal


def create_initial_cockpit_state() -> dict[str, Any]:
    return {
        'version': 1,
        'vehicle': {'ac': False, 'preconditioning': False, 'acTemp': 22,
                    'passengerTemp': 22, 'rearTemp': 22, 'acMode': 'cool', 'acFan': 3,
                    'windows': dict.fromkeys(['windowFL', 'windowFR', 'windowRL', 'windowRR'], 0),
                    'sunroof': 'closed', 'closures': {}, 'comfort': {}, 'headlights': False,
                    'hornCount': 0, 'charging': False, 'chargeLimit': 80, 'chargingAmps': 16,
                    'chargeMode': 'standard', 'chargeSchedules': []},
        'location': {'address': '演示车位', 'source': 'offline-demo'},
        'navigation': {'status': 'idle', 'destination': None, 'waypoints': [], 'strategy': 0,
                       'route': None, 'favorites': {}, 'muted': False,
                       'broadcastMode': 'standard', 'viewMode': 'follow'},
        'music': {'playing': False, 'currentIndex': 0, 'volume': 5, 'muted': False,
                  'source': 'qq_music', 'favoriteIds': [], 'results': []},
        'weather': {},
        'flashbuy': {'status': 'idle', 'results': [], 'cartItems': [], 'preview': None, 'order': None},
    }


class CockpitStateStore:
    def __init__(self) -> None:
        self.records: dict[str, dict[str, Any]] = {}
        self.events = Signal()

    def snapshot(self, cockpit_id: str = 'default') -> dict[str, Any]:
        self.records.setdefault(cockpit_id, create_initial_cockpit_state())
        return deepcopy(self.records[cockpit_id])

    def update(self, cockpit_id: str, changed: list[str],
               mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        state = self.snapshot(cockpit_id)
        mutate(state)
        state['version'] += 1
        self.records[cockpit_id] = state
        self.events.emit({'type': 'state', 'cockpitId': cockpit_id,
                          'changed': changed, 'state': state, 'version': state['version']})
        return deepcopy(state)

    def subscribe(self, cockpit_id: str, listener: Callable) -> Callable[[], None]:
        def scoped(event: dict[str, Any]) -> None:
            if event['cockpitId'] == cockpit_id:
                listener(event)
        return self.events.subscribe(scoped)

    def reset(self, cockpit_id: str = 'default') -> dict[str, Any]:
        self.records[cockpit_id] = create_initial_cockpit_state()
        state = self.snapshot(cockpit_id)
        self.events.emit({'type': 'state', 'cockpitId': cockpit_id, 'changed': list(state),
                          'state': state, 'version': state['version']})
        return state
