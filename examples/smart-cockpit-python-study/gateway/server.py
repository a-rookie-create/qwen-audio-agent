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
    config = write_cockpit_frontend_profile_bundle(service.service.registry.definitions_for('frontend'))
    adapter = create_backend_agent_host(A2ABackendAdapter(agent, trace))
    gateway = create_gateway_application(adapter, service, config, trace)
    trace.record('Composition', 'spawn_policy', create_cockpit_spawn_thinking_description(service.service.registry.routing))
    gateway.start()
    return gateway
