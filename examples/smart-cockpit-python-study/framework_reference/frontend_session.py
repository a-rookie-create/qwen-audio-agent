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
        # 前台业务工具经过前台 MCP 面检查，再由同一 Service 执行真正的状态更新。
        return await self.server.call_tool(name, arguments)


class DemoRealtimeModel:
    """本地规则模型，只模拟模型事件选择；没有声称完成真实语音推理。"""
    def __init__(self, config: GatewayConfig) -> None:
        self.profile_id, self.profile_text = config.profile_id, config.profile_text
        self.environment: dict[str, dict] = {}

    def plan(self, text: str) -> ModelReply:
        # 规则匹配只生成 ToolCall 描述，还没有执行工具；执行由 ToolCallHandler 完成。
        if text.startswith('记住'):
            return ModelReply(tool_calls=[ToolCall('memory_write', {'text': text[2:]})])
        calls: list[ToolCall] = []
        # 各意图可以同时命中，保留成有序调用列表，例如空调 + 音乐 + 后台委派。
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
        # 只把命中的那一小句作为后台目标，前台已识别的车控/音乐仍在前台执行。
        objective = next((s for s in pieces if any(k in s for k in ('咖啡', '拿铁', '确认下单', '研究', '新闻'))), '')
        if objective:
            calls.append(ToolCall('spawn_thinking', {'objective': objective}))
        if calls:
            return ModelReply(tool_calls=calls)
        # 没有工具调用时直接生成聊天回复；导航偏好来自先前收到的上下文事件。
        if '路线偏好' in text and 'cockpit.navigation.preference_changed' in self.environment:
            strategy = self.environment['cockpit.navigation.preference_changed']['strategy']
            return ModelReply('当前路线策略编号：' + str(strategy))
        return ModelReply('你好，我是离线座舱学习助手。')

    def summarize(self, results: list[ToolResult]) -> str:
        # 回复基于真实工具返回文本，错误结果也会显示，避免把失败写成成功。
        return '；'.join(result.content for result in results)


class ToolCallHandler:
    def __init__(self, session: RealtimeSessionRuntime) -> None:
        self.session = session

    async def handle(self, call: ToolCall) -> ToolResult:
        session = self.session
        session.trace.record('Frontend', 'tool_call', call.name)
        if call.name == 'spawn_thinking':
            # submit 只接受并排队任务，立即返回 ID；后台结果稍后经协调器送回会话。
            task = session.operations.submit(call.arguments['objective'], session.owner_id, session.session_id)
            return ToolResult('后台工作已开始，你可以继续聊天。', {'task_id': task.id, 'receipt': 'accepted'})
        if call.name == 'memory_write':
            # 记忆由 Gateway Provider 按用户保存，与 Service 的车辆/技能状态分开。
            session.memory.apply(session.owner_id, [{'operation': 'add', 'text': call.arguments['text']}])
            session.send({'type': 'memory.changed'})
            return ToolResult('已保存记忆')
        # 其余调用属于业务工具，交给前台 MCP 工具源执行。
        return await session.tools.execute(call.name, call.arguments)


class RealtimeSessionRuntime:
    def __init__(self, owner_id: str, session_id: str, send: Callable[[dict], None],
                 operations: TaskOperations, tools: FrontendMcpToolSource, config: GatewayConfig,
                 memory: MemoryProvider, trace: TraceLog) -> None:
        self.owner_id, self.session_id, self.send = owner_id, session_id, send
        self.operations, self.tools, self.memory, self.trace = operations, tools, memory, trace
        self.model = DemoRealtimeModel(config)
        # 每次连接都有自己的模型上下文、静音状态和工具处理器；共享服务由外部传入。
        self.tool_handler = ToolCallHandler(self)
        self.muted, self.closed = False, False
        self.coordinator: SessionTaskCoordinator | None = None

    async def handle_input(self, text: str) -> dict:
        if self.closed:
            raise RuntimeError('会话已关闭')
        self.trace.record('Session', 'input', text)
        reply = self.model.plan(text)
        # 先规划，再依次执行。没有 tool_calls 时下面循环跳过，直接发送聊天内容。
        calls = list(reply.tool_calls)
        results: list[ToolResult] = []
        for index in range(8):
            # 单次输入最多执行八个工具，限制工作流展开后的调用量。
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
        # 普通回复与 accepted 回执都使用 reply；task_ids 让客户端能等待后台结果。
        message = {'type': 'reply', 'text': self.model.summarize(results) if results else reply.content,
                   'task_ids': [r.data['task_id'] for r in results if 'task_id' in r.data]}
        self.send(message)  # send 是连接时传入的客户端回调，这里实际调用它。
        return message

    async def handle_client_event(self, event: dict) -> dict:
        # 根据事件 type 分派入口：用户输入、静音控制、环境事实各走自己的逻辑。
        event_type = event['type']
        if event_type == 'input.message':
            return await self.handle_input(event['text'])
        if event_type == 'audio.append':
            # 演示音频为 UTF-8 文本字节，仅用于展示调用路径，不是 PCM 或 ASR。
            return await self.handle_input(event['audio'].decode('utf-8'))
        if event_type in {'mute', 'unmute'}:
            self.muted = event_type == 'mute'
            # unmute 后协调器尝试投递积压结果；mute 时 refresh 会直接返回。
            if self.coordinator:
                self.coordinator.refresh()
            return {'accepted': True}
        if event_type == 'client.event.publish':
            # 事件名映射到校验函数，返回的 mode 决定更新人设、上下文还是发送提醒。
            handler = CLIENT_EVENT_DEFINITIONS[event['name']]
            delivery = handler(event)
            if delivery.mode == 'handle':
                # 人设文本替换本会话模型配置，不创建任务或执行工具。
                self.model.profile_id, self.model.profile_text = delivery.profile_id, delivery.text
            elif delivery.mode == 'context':
                # 静默保存最新事实，后续回答可以读取它；不会立即发聊天回复。
                self.model.environment[delivery.name] = delivery.data or {}
            else:
                # 提醒直接作为环境来源的回复发送，文本不会再进入工具规划。
                self.send({'type': 'reply', 'text': delivery.text, 'origin': 'environment'})
            return {'accepted': True}
        raise ValueError('未知客户端事件')

    def can_announce(self) -> bool:
        # 学习版的播报门槛仅检查关闭与静音状态。
        return not self.closed and not self.muted

    async def present_task_result(self, task: TaskRecord) -> bool:
        # 协调器调用此方法时再次检查可用性，防止排队等待期间会话已关闭或静音。
        if not self.can_announce():
            return False
        self.trace.record('Session', 'announce_result', task.id)
        self.send({'type': 'reply', 'text': task.result.content if task.result else '',
                   'task_id': task.id, 'origin': 'background'})
        return True  # 只表示回复已送出；delivered 还需要客户端的播放确认。

    async def close(self) -> None:
        # 关闭当前会话的通知协调器，后台工作的生命周期仍由共享 TaskManager 管理。
        self.closed = True
        if self.coordinator:
            await self.coordinator.close()
