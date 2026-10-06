"""前台模型、工具处理器和每连接会话；这里真正执行三条请求分支。"""
from __future__ import annotations
import re
from typing import Callable
from service.mcp_server import CockpitMcpServer
from study_support import ModelReply, ToolCall, ToolResult, TraceLog
from framework_reference.extension_ports import MemoryProvider
from framework_reference.task_runtime import TaskOperations, TaskRecord, SessionTaskCoordinator
from gateway.environment_events import CLIENT_EVENT_DEFINITIONS
from gateway.profile_bundle import GatewayConfig


class FrontendMcpToolSource:
    def __init__(self, server: CockpitMcpServer) -> None:
        self.server = server

    async def execute(self, name: str, arguments: dict) -> ToolResult:
        return await self.server.call_tool(name, arguments)


class DemoRealtimeModel:
    """本地规则模型，只模拟模型事件选择；没有声称完成真实语音推理。"""
    def __init__(self, config: GatewayConfig) -> None:
        self.profile_id, self.profile_text = config.profile_id, config.profile_text
        self.environment: dict[str, dict] = {}

    def plan(self, text: str) -> ModelReply:
        if text.startswith('记住'):
            return ModelReply(tool_calls=[ToolCall('memory_write', {'text': text[2:]})])
        calls: list[ToolCall] = []
        temperature = re.search(r'(\d+(?:\.\d+)?)\s*度', text)
        if temperature and ('空调' in text or '温度' in text):
            calls.append(ToolCall('vehicle_temperature_control', {'action': 'set', 'temperature': float(temperature[1]), 'zone': 'all'}))
        elif '空调' in text and ('当前' in text or '多少' in text):
            calls.append(ToolCall('vehicle_state_query'))
        music = re.search(r'播放([^，。；]+)', text)
        if music:
            calls.append(ToolCall('music_play', {'query': music[1].strip()}))
        destination = re.search(r'导航到([^，。；]+)', text)
        if destination:
            calls.append(ToolCall('navigation_start', {'destination': destination[1].strip()}))
        if '天气' in text:
            calls.append(ToolCall('weather', {'city': '杭州'}))
        skill = re.search(r'(?:运行|加载)(.+?)(?:技能|$)', text)
        if skill:
            calls.append(ToolCall('custom_skill_load', {'skill_name': skill[1].strip()}))
        pieces = re.split('[，。；]', text)
        objective = next((s for s in pieces if any(k in s for k in ('咖啡', '拿铁', '确认下单', '研究', '新闻'))), '')
        if objective:
            calls.append(ToolCall('spawn_thinking', {'objective': objective}))
        if calls:
            return ModelReply(tool_calls=calls)
        if '路线偏好' in text and 'cockpit.navigation.preference_changed' in self.environment:
            strategy = self.environment['cockpit.navigation.preference_changed']['strategy']
            return ModelReply('当前路线策略编号：' + str(strategy))
        return ModelReply('你好，我是离线座舱学习助手。')

    def summarize(self, results: list[ToolResult]) -> str:
        return '；'.join(result.content for result in results)


class ToolCallHandler:
    def __init__(self, session: RealtimeSessionRuntime) -> None:
        self.session = session

    async def handle(self, call: ToolCall) -> ToolResult:
        session = self.session
        session.trace.record('Frontend', 'tool_call', call.name)
        if call.name == 'spawn_thinking':
            task = session.operations.submit(call.arguments['objective'], session.owner_id, session.session_id)
            return ToolResult('后台工作已开始，你可以继续聊天。', {'task_id': task.id, 'receipt': 'accepted'})
        if call.name == 'memory_write':
            session.memory.apply(session.owner_id, [{'operation': 'add', 'text': call.arguments['text']}])
            session.send({'type': 'memory.changed'})
            return ToolResult('已保存记忆')
        return await session.tools.execute(call.name, call.arguments)


class RealtimeSessionRuntime:
    def __init__(self, owner_id: str, session_id: str, send: Callable[[dict], None],
                 operations: TaskOperations, tools: FrontendMcpToolSource, config: GatewayConfig,
                 memory: MemoryProvider, trace: TraceLog) -> None:
        self.owner_id, self.session_id, self.send = owner_id, session_id, send
        self.operations, self.tools, self.memory, self.trace = operations, tools, memory, trace
        self.model = DemoRealtimeModel(config)
        self.tool_handler = ToolCallHandler(self)
        self.muted, self.closed = False, False
        self.coordinator: SessionTaskCoordinator | None = None

    async def handle_input(self, text: str) -> dict:
        if self.closed:
            raise RuntimeError('会话已关闭')
        self.trace.record('Session', 'input', text)
        reply = self.model.plan(text)
        calls = list(reply.tool_calls)
        results: list[ToolResult] = []
        for index in range(8):
            if not calls:
                break
            call = calls.pop(0)
            result = await self.tool_handler.handle(call)
            results.append(result)
            if call.name == 'custom_skill_load' and '运行' in text and not result.is_error:
                skill = result.data['skill']
                if skill['kind'] == 'workflow':
                    # 保存的工作流由现有前台/后台工具协调执行，不注册新 MCP 工具。
                    calls.extend(self.model.plan(skill['instructions']).tool_calls)
        message = {'type': 'reply', 'text': self.model.summarize(results) if results else reply.content,
                   'task_ids': [r.data['task_id'] for r in results if 'task_id' in r.data]}
        self.send(message)
        return message

    async def handle_client_event(self, event: dict) -> dict:
        event_type = event['type']
        if event_type == 'input.message':
            return await self.handle_input(event['text'])
        if event_type == 'audio.append':
            # 演示音频为 UTF-8 文本字节，仅用于展示调用路径，不是 PCM 或 ASR。
            return await self.handle_input(event['audio'].decode('utf-8'))
        if event_type in {'mute', 'unmute'}:
            self.muted = event_type == 'mute'
            if self.coordinator:
                self.coordinator.refresh()
            return {'accepted': True}
        if event_type == 'client.event.publish':
            handler = CLIENT_EVENT_DEFINITIONS[event['name']]
            delivery = handler(event)
            if delivery.mode == 'handle':
                self.model.profile_id, self.model.profile_text = delivery.profile_id, delivery.text
            elif delivery.mode == 'context':
                self.model.environment[delivery.name] = delivery.data or {}
            else:
                self.send({'type': 'reply', 'text': delivery.text, 'origin': 'environment'})
            return {'accepted': True}
        raise ValueError('未知客户端事件')

    def can_announce(self) -> bool:
        return not self.closed and not self.muted

    async def present_task_result(self, task: TaskRecord) -> bool:
        if not self.can_announce():
            return False
        self.trace.record('Session', 'announce_result', task.id)
        self.send({'type': 'reply', 'text': task.result.content if task.result else '',
                   'task_id': task.id, 'origin': 'background'})
        return True

    async def close(self) -> None:
        self.closed = True
        if self.coordinator:
            await self.coordinator.close()
