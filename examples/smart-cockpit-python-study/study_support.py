"""真实的数据类型和事件订阅工具；没有未定义的伪操作。"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any, Callable


# dataclass 根据下面的字段自动生成 __init__ 等方法；这些类用于组件之间传递数据。
@dataclass
class ToolDefinition:
    # 模型根据说明和参数 Schema 选择工具；domain/surface 决定执行器与前后台归属。
    name: str
    description: str
    input_schema: dict[str, Any]
    domain: str
    surface: str


@dataclass
class ToolResult:
    content: str
    # 每个实例各建一个 dict/list，避免不同工具结果共用同一份可变数据。
    data: dict[str, Any] = field(default_factory=dict)
    changed: list[str] = field(default_factory=list)
    state_version: int = 0
    is_error: bool = False


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    # 为每次调用生成独立 ID，后续工具结果用这个 ID 对应模型提出的调用。
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class ModelReply:
    # 有 tool_calls 表示模型请求执行工具；没有调用时，content 就是最终回复。
    content: str = ''
    tool_calls: list[ToolCall] = field(default_factory=list)


class TraceLog:
    """收集调用顺序，便于在 main.py --trace 中看到跨模块调用链。"""
    def __init__(self) -> None:
        self.entries: list[tuple[str, str, str]] = []

    def record(self, component: str, action: str, detail: str = '') -> None:
        # 这里只记录发生过的调用，不驱动执行；列表顺序用于还原实际调用链。
        self.entries.append((component, action, detail))


class Signal:
    """同步发布事实事件；需异步处理的订阅者自行创建 asyncio Task。"""
    def __init__(self) -> None:
        # 列表中存的是回调函数。subscribe 注册函数，emit 才调用这些函数。
        self.listeners: list[Callable[[dict[str, Any]], None]] = []
        self.errors: list[Exception] = []

    def subscribe(self, listener: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        self.listeners.append(listener)
        # def 只是定义函数，此处不会删除 listener。
        # 这个内部函数记住本次传入的 listener，调用它时才取消该订阅。
        def unsubscribe() -> None:
            if listener in self.listeners:
                self.listeners.remove(listener)
        return unsubscribe  # 返回函数本身；调用方通常保存为 cancel，之后执行 cancel()。

    def emit(self, event: dict[str, Any]) -> None:
        # tuple 固定本次要通知的名单，避免回调增删原列表影响这一轮遍历。
        # listener 是元组中的一个函数；本轮期间取消的订阅仍在这份名单中。
        for listener in tuple(self.listeners):
            try:
                # 调用回调并传入独立副本；一个订阅者修改事件不会影响其他订阅者。
                listener(deepcopy(event))
            except Exception as error:
                self.errors.append(error)  # 观察者错误不撤销已完成的状态更新。


def tool_result(content: str, state: dict[str, Any], changed: list[str] | None = None,
                data: dict[str, Any] | None = None) -> ToolResult:
    # 包装已完成的业务结果并带上版本号；changed 描述变化，不负责修改状态。
    return ToolResult(content, data or {}, changed or [], state['version'])
