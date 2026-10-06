"""真实的数据类型和事件订阅工具；没有未定义的伪操作。"""
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: dict[str, Any]
    domain: str
    surface: str


@dataclass
class ToolResult:
    content: str
    data: dict[str, Any] = field(default_factory=dict)
    changed: list[str] = field(default_factory=list)
    state_version: int = 0
    is_error: bool = False


@dataclass
class ToolCall:
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class ModelReply:
    content: str = ''
    tool_calls: list[ToolCall] = field(default_factory=list)


class TraceLog:
    """收集调用顺序，便于在 main.py --trace 中看到跨模块调用链。"""
    def __init__(self) -> None:
        self.entries: list[tuple[str, str, str]] = []

    def record(self, component: str, action: str, detail: str = '') -> None:
        self.entries.append((component, action, detail))


class Signal:
    """同步发布事实事件；需异步处理的订阅者自行创建 asyncio Task。"""
    def __init__(self) -> None:
        self.listeners: list[Callable[[dict[str, Any]], None]] = []
        self.errors: list[Exception] = []

    def subscribe(self, listener: Callable[[dict[str, Any]], None]) -> Callable[[], None]:
        self.listeners.append(listener)
        def unsubscribe() -> None:
            if listener in self.listeners:
                self.listeners.remove(listener)
        return unsubscribe

    def emit(self, event: dict[str, Any]) -> None:
        for listener in tuple(self.listeners):
            try:
                listener(deepcopy(event))
            except Exception as error:
                self.errors.append(error)  # 观察者错误不撤销已完成的状态更新。


def tool_result(content: str, state: dict[str, Any], changed: list[str] | None = None,
                data: dict[str, Any] | None = None) -> ToolResult:
    return ToolResult(content, data or {}, changed or [], state['version'])
