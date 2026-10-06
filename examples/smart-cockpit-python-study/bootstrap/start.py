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


@dataclass
class StudyRuntime:
    trace: TraceLog
    service: CockpitServiceServer
    agent: CockpitAgentServer
    gateway: GatewayApplication
    app: CockpitApp

    async def close(self) -> None:
        await self.app.close()
        await self.gateway.close()


async def build_study_runtime(model: ChatModel | None = None, data_dir: Path | None = None,
                              owner_id: str = 'demo-user', session_id: str = 'main',
                              cockpit_id: str = 'default') -> StudyRuntime:
    env = load_cockpit_environment()
    trace = TraceLog()
    service = CockpitServiceServer(CockpitService(trace, data_dir))
    tools = CockpitAgentTools(CockpitMcpTools(service.mcp('backend', cockpit_id)), WebRetrieval())
    executor = CockpitAgentExecutor(model or DemoChatModel(float(env.get('STUDY_MODEL_DELAY', '0.02'))), tools, trace)
    agent = start_cockpit_agent_server(executor)
    gateway = start_cockpit_gateway(service, agent, trace)
    app = CockpitApp(gateway, service, owner_id, session_id, cockpit_id)
    app.start()
    await app.voice.flush()
    return StudyRuntime(trace, service, agent, gateway, app)


async def start_four_processes() -> StudyRuntime:
    # 保留旧学习入口名方便对照；这里不启动四个 OS 进程。
    return await build_study_runtime()
