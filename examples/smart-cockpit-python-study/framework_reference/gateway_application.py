"""真实对象装配与每连接会话工厂；传输在学习版中采用方法调用。"""
from __future__ import annotations
from typing import Callable
from framework_reference.backend_adapter import A2ABackendAdapter, BackendWorkRuntime
from framework_reference.task_runtime import TaskManager, TaskOperations, SessionTaskCoordinator
from framework_reference.frontend_session import RealtimeSessionRuntime, FrontendMcpToolSource
from framework_reference.extension_ports import MemoryProvider
from gateway.profile_bundle import GatewayConfig
from service.server import CockpitServiceServer
from study_support import TraceLog


class GatewayApplication:
    def __init__(self, agent: A2ABackendAdapter, service: CockpitServiceServer,
                 config: GatewayConfig, trace: TraceLog) -> None:
        self.service, self.config, self.trace = service, config, trace
        # 应用级共享对象：任务状态归 TaskManager，Agent 执行通过 BackendWorkRuntime。
        self.tasks = TaskManager(trace)
        self.backend = BackendWorkRuntime(agent)
        self.operations = TaskOperations(self.tasks, self.backend)
        self.memory = MemoryProvider()
        # 用户与会话 ID 共同组成键；同一应用可连接多个各自独立的前台会话。
        self.sessions: dict[tuple[str, str], RealtimeSessionRuntime] = {}
        self.started = False

    def start(self) -> None:
        # 学习版只打开连接许可，不监听网络端口。
        self.started = True
        self.trace.record('Gateway', 'start', 'in-process transport')

    def connect(self, owner_id: str, session_id: str, send: Callable[[dict], None],
                cockpit_id: str = 'default') -> RealtimeSessionRuntime:
        if not self.started:
            raise RuntimeError('Gateway 尚未启动')
        key = (owner_id, session_id)
        if key in self.sessions and not self.sessions[key].closed:
            raise ValueError('会话已经连接')
        # 每次连接新建会话，但传入共享任务操作与记忆；工具面绑定本次 cockpit_id。
        session = RealtimeSessionRuntime(owner_id, session_id, send, self.operations,
            FrontendMcpToolSource(self.service.mcp('frontend', cockpit_id)), self.config, self.memory, self.trace)
        # 协调器把共享任务事件过滤到本会话，并在会话可用时投递后台结果。
        session.coordinator = SessionTaskCoordinator(self.tasks, session)
        self.sessions[key] = session
        self.trace.record('Gateway', 'create_session', session_id)
        return session

    async def memory_request(self, owner_id: str, method: str, body: dict | None = None) -> dict:
        # 模拟记忆 HTTP 边界；Provider 统一负责用户隔离、版本检查和实际保存。
        if method == 'GET':
            return {'documents': self.memory.list(owner_id)}
        if method == 'PATCH':
            return {'documents': self.memory.apply(owner_id, (body or {})['changes'])}
        raise ValueError('未知记忆方法')

    async def close(self) -> None:
        # 先关闭会话，停止结果投递；再取消共享后台任务，防止关机期间继续发送消息。
        for session in self.sessions.values():
            await session.close()
        await self.tasks.close()
        self.started = False


def create_gateway_application(agent: A2ABackendAdapter, service: CockpitServiceServer,
                               config: GatewayConfig, trace: TraceLog) -> GatewayApplication:
    # 工厂只创建对象，start_cockpit_gateway 随后显式调用 start 开放连接。
    return GatewayApplication(agent, service, config, trace)
