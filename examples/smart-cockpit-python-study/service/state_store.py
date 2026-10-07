"""业务状态的唯一来源；同一个更新事件同时驱动 UI 和规则观察器。"""
from __future__ import annotations
from copy import deepcopy
from typing import Any, Callable
from study_support import Signal


def create_initial_cockpit_state() -> dict[str, Any]:
    # 每次调用都新建一套嵌套字典和列表，保证不同车机、重置前后的状态互不共享。
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
        # cockpit_id -> 当前权威状态；客户端和工具拿到的是它的副本。
        self.records: dict[str, dict[str, Any]] = {}
        # events 只通知已发生的更新；真正的状态修改在 update/reset 中完成。
        self.events = Signal()

    def snapshot(self, cockpit_id: str = 'default') -> dict[str, Any]:
        # setdefault 只在 ID 不存在时写入初始值，已有记录会保留。
        self.records.setdefault(cockpit_id, create_initial_cockpit_state())
        # 连嵌套字典一起复制，调用方直接修改返回值也不会改动 records。
        return deepcopy(self.records[cockpit_id])

    def update(self, cockpit_id: str, changed: list[str],
               mutate: Callable[[dict[str, Any]], None]) -> dict[str, Any]:
        # Callable[[参数类型], 返回类型] 描述函数：这里接收一个字典，返回 None。
        # 标注中的 [dict[str, Any]] 是参数类型列表，不是实际传入的列表或字典。
        # 先在副本上执行传入的修改函数；mutate 报错时不会提交这份修改。
        # mutate 是函数参数，例如 lambda state: state['vehicle'].update(changes)。
        state = self.snapshot(cockpit_id)
        mutate(state)
        # 修改成功后增加版本并保存。changed 由调用者提供，是变化领域的名单。
        state['version'] += 1
        self.records[cockpit_id] = state
        # 保存之后再同步通知 UI/规则观察器，订阅者读到的已是新状态。
        self.events.emit({'type': 'state', 'cockpitId': cockpit_id,
                          'changed': changed, 'state': state, 'version': state['version']})
        return deepcopy(state)  # 返回副本，继续保护内部保存的权威状态。

    def subscribe(self, cockpit_id: str, listener: Callable) -> Callable[[], None]:
        # 共用一个 Signal，但包装函数会过滤 ID，避免其他车机的事件串过来。
        def scoped(event: dict[str, Any]) -> None:
            if event['cockpitId'] == cockpit_id:
                listener(event)
        return self.events.subscribe(scoped)  # 返回取消 scoped 订阅的函数，暂时不调用。

    def reset(self, cockpit_id: str = 'default') -> dict[str, Any]:
        # 重置会恢复整套初始值（version 也回到 1），而非继续递增旧版本。
        self.records[cockpit_id] = create_initial_cockpit_state()
        state = self.snapshot(cockpit_id)
        # list(state) 取全部顶层键，告诉客户端各领域都需要重新读取。
        self.events.emit({'type': 'state', 'cockpitId': cockpit_id, 'changed': list(state),
                          'state': state, 'version': state['version']})
        return state
