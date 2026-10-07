"""座舱装配入口：配置、后台 Adapter 与框架 Gateway 在这里连接。"""
from agent.server import CockpitAgentServer
from service.server import CockpitServiceServer
from framework_reference.backend_adapter import A2ABackendAdapter, create_backend_agent_host
from framework_reference.gateway_application import GatewayApplication, create_gateway_application
from gateway.profile_bundle import write_cockpit_frontend_profile_bundle
from gateway.spawn_thinking_tool import create_cockpit_spawn_thinking_description
from study_support import TraceLog


def start_cockpit_gateway(service: CockpitServiceServer, agent: CockpitAgentServer,
                          trace: TraceLog) -> GatewayApplication:
    # 先取业务服务的前台工具目录和人设，生成当前座舱的框架配置。
    config = write_cockpit_frontend_profile_bundle(service.service.registry.definitions_for('frontend'))
    # 通过适配器接入后台 Agent，Gateway 只依赖统一提交/取消接口。
    adapter = create_backend_agent_host(A2ABackendAdapter(agent, trace))
    gateway = create_gateway_application(adapter, service, config, trace)
    # 委派描述记录在 trace 供学习观察；真正工具归属仍由注册表和 MCP 面检查。
    trace.record('Composition', 'spawn_policy', create_cockpit_spawn_thinking_description(service.service.registry.routing))
    gateway.start()  # 装配完成后开放连接，随后客户端才能创建自己的会话。
    return gateway
