"""真正的装配入口：原四进程角色在学习版中组装为同一进程内的四组对象。"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from study_support import TraceLog
from service.cockpit_service import CockpitService
from service.server import CockpitServiceServer
from agent.model import ChatModel, DemoChatModel
from agent.tools import CockpitAgentTools
from agent.mcp_client import CockpitMcpTools
from agent.executor import CockpitAgentExecutor
from agent.server import CockpitAgentServer, start_cockpit_agent_server
from framework_reference.extension_ports import WebRetrieval
from framework_reference.gateway_application import GatewayApplication
from gateway.server import start_cockpit_gateway
from client.app import CockpitApp
from bootstrap.environment import load_cockpit_environment


# 自动生成接收这五个字段的构造方法；StudyRuntime 把装配好的组件集中保存。
@dataclass
class StudyRuntime:
    trace: TraceLog
    service: CockpitServiceServer
    agent: CockpitAgentServer
    gateway: GatewayApplication
    app: CockpitApp

    async def close(self) -> None:
        # 先取消客户端订阅、关闭会话，再由 Gateway 清理剩余后台任务。
        await self.app.close()
        await self.gateway.close()


# 这是类外的模块级异步函数。-> StudyRuntime 标注返回类型，不表示类方法。
async def build_study_runtime(model: ChatModel | None = None, data_dir: Path | None = None,
                              owner_id: str = 'demo-user', session_id: str = 'main',
                              cockpit_id: str = 'default') -> StudyRuntime:
    env = load_cockpit_environment()
    # 所有组件共用同一个 trace，才能在演示里按实际顺序展示跨组件调用。
    trace = TraceLog()
    # 1. 创建业务服务：它拥有状态和技能；外层 Server 提供查询、订阅与工具入口。
    service = CockpitServiceServer(CockpitService(trace, data_dir))
    # 2. 创建后台 Agent：只接后台 MCP 工具面，再组合独立的网页检索能力。
    tools = CockpitAgentTools(CockpitMcpTools(service.mcp('backend', cockpit_id)), WebRetrieval())
    # 可注入模型用于测试或扩展；未传入时使用带模拟延迟的离线规则模型。
    executor = CockpitAgentExecutor(model or DemoChatModel(float(env.get('STUDY_MODEL_DELAY', '0.02'))), tools, trace)
    agent = start_cockpit_agent_server(executor)
    # 3. Gateway 接入同一 Service 和 Agent，持有任务管理器等共享对象。
    gateway = start_cockpit_gateway(service, agent, trace)
    # 4. 客户端分别连接 Gateway 会话和 Service 状态订阅，两条通路各司其职。
    app = CockpitApp(gateway, service, owner_id, session_id, cockpit_id)
    app.start()
    # 启动订阅会收到初始状态，并排入导航上下文事件；等待这些事件送达再返回。
    await app.voice.flush()
    # 构造数据类实例，调用者可通过 runtime.app/service 等访问已连接的组件。
    return StudyRuntime(trace, service, agent, gateway, app)


async def start_four_processes() -> StudyRuntime:
    # 保留旧学习入口名方便对照；这里不启动四个 OS 进程。
    return await build_study_runtime()
