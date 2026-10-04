# 专题：客户端、协议与扩展入口

[返回伴读入口](../README.md) · 关联：[架构与装配](../03-architecture-and-entrypoints.md)

## 1. 多个客户端复用的是服务契约

| 客户端 | 核心职责 | 第一次阅读入口 |
| --- | --- | --- |
| WebUI | 麦克风、文本图片与视频输入、消息 / Task 展示、音频播放 | [useRealtimeVoice](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/useRealtimeVoice.js#L203)、[App.jsx](../../../web/src/App.jsx) |
| Desktop | Electron 生命周期、窗口、配置、本地唤醒与 Gateway 连接 | [startConfiguredRuntime / Electron main](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/desktop/src/main.mjs#L390)、[DesktopWakeWordRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/desktop/src/wake-word/runtime.mjs#L3)、[preload](../../../desktop/src/preload.cjs) |
| TUI | 终端输入、附件、命令与平台音频 | [runTui](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/tui/src/index.mjs#L141)、[输入附件](../../../tui/src/input-parts.mjs) |
| Mobile | 复用 Web 界面并桥接原生存储、权限和设备接入 | [main.jsx](../../../mobile/src/main.jsx)、[native-runtime](../../../mobile/src/native-runtime.js) |

共用基础包括 [GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63) 和 [reduceGatewayClientState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-state.mjs#L29)。客户端不应导入服务端 TaskManager 或另一个客户端的业务实现来操作服务。模型判断和权限策略由运行时承担；麦克风权限、窗口和声音设备由客户端环境管理。

## 2. 用协议理解“连接成功”

[GATEWAY_CLIENT_PROTOCOL_VERSION / protocol definitions](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/protocol/gateway-client-protocol.mjs#L13) 定义当前线版本 `7.0.0`、事件、能力和 schema；[协议手册](../../gateway-protocol.zh.md)说明访问边界、握手、命令和投影。

接入身份认证发生在 GCP 会话业务之前。客户端通过 `session.hello` 声明版本范围、能力与环境，收到 `session.ready` 后才完成会话握手。GatewayClient 管请求关联、超时、重连和待处理请求；不能用 Socket open 回调替代所有就绪判断。

当前契约每个已认证 owner 同一时刻只有一个活动 Client Environment；新连接可能因占用被拒绝，显式接管另有语义。默认个人部署表现为一个活动客户端。不要把“支持 Web、手机、TUI”直接推导成它们可同时作为活动输入端。

网络访问凭据与模型 API Key 是两类凭据；一个成功不能证明另一个正确。这里的差异是实际接入流程，详见 [GatewayAccessManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/access/gateway-access.mjs#L245) 与 [attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62)。

## 3. Event 与 Action 的区别

Client Event 表达环境发生了什么，例如摄像头状态或其他设备变化。Gateway 根据注册的语义决定确定性处理、只更新上下文、延迟或立即回应。

Client Action 表达要环境执行什么，必须有结果返回，例如进入桌面休眠。模型调用的工具可以映射为 Client Action；不能让模型直接把任意客户端文本当成 Gateway 权限或 Task 生命周期事件。

实现看[事件路由](../../../server/src/client/client-event-router.mjs)与[ClientActionPort](../../../server/src/client/client-action-port.mjs)。数据投递还有与 Provider 无关的 AgentDelivery；它和传输协议事件也不是同一种对象。

## 4. WebSocket 与 WebRTC 在哪层不同

默认 GCP WebSocket 路径携带控制和音频事件。可选 WebRTC 增加媒体会话、音频轨道与配套控制入口，但仍使用 Gateway 的认证、客户端归属、会话运行时和工作语义。

具体代码在[WebRTC routes](../../../server/src/transport/webrtc/routes.mjs)、[媒体进程](../../../server/src/transport/webrtc/media-process.mjs)与[浏览器 transport](../../../shared/gateway/webrtc-browser.mjs)；操作说明见[WebRTC 客户端](../../gateway-webrtc-client.zh.md)。媒体处理的依赖和运行需求不应默认归入每个普通 Gateway 启动。

本次没有运行真实 WebRTC 或媒体设备；静态验证表明其入口可接入共享运行时，不能据此断言任何网络下延迟或稳定性。

## 5. 想扩展什么，就选择对应边界

| 要实现的能力 | 合适入口 | 需要保持的契约 |
| --- | --- | --- |
| 新实时语音模型 | Realtime Provider | Session 配置、音频、工具、事件与错误语义 |
| 新办事 Agent | BackendPort Adapter / SDK | submit、cancel、授权、输入、事件、产物、关闭 |
| 前台业务查询或轻工具 | MCP / OpenAPI tool source 或已定义工具入口 | schema、能力、执行校验、结果大小与失败 |
| 新知识检索服务 | Knowledge Provider | retrieve 与归一化资料片段；管理方法按能力提供 |
| 新记忆服务 | Memory Provider | 同步快照、写入、可选观察能力与热路径限制 |
| 新界面 / 设备 | GCP / GatewayClient | 身份、握手、能力、命令、事件与播放事实 |
| 新业务宿主 | createGatewayApplication | 明确注入规则、Provider、后台和客户端事件定义 |

依据：[RealtimeProviderRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/providers/provider-registry.mjs#L261)、[BACKEND_PORT_METHODS / assertBackendPort](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/backend-port.mjs#L22)、[assertFrontendToolSource](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-source.mjs#L12)、[assertKnowledgeRetrievalProvider](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/provider.mjs#L156)、[assertMemoryProvider / provider contract](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/provider.mjs#L76)、[GATEWAY_CLIENT_PROTOCOL_VERSION / protocol definitions](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/protocol/gateway-client-protocol.mjs#L13)、[createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)。

若接入 MCP，区分**前台 MCP**和**后台 Agent 自己的 MCP**。前者让实时模型可调用低延迟业务工具；后者属于办事 Agent 执行环境。ACP 内部的协调 MCP 又服务于后台 Session 委派，不能把三者视为一份工具列表。

## 6. 只会 Python，也能从边界参与

你最容易先掌握框架行为，再把熟悉的 Python 能力做成独立服务。需要一个小的 Node 适配层把 HTTP / MCP 响应转成框架对象；不需要立刻重写整个语音或桌面系统。

三个可循序实践的方向：

1. **知识查询：**读[LightRAG 示例](../../../examples/lightrag/README_ZH.md)、[lightrag-provider.mjs](../../../examples/lightrag/lightrag-provider.mjs)和 Gateway 注入。先理解 Python 服务与 Node Adapter 的责任分工。
2. **记忆服务：**读[VoiceMem 示例](../../../examples/voicemem/README_ZH.md)及[Python sidecar](../../../examples/voicemem/sidecar/server.py)。重点是快照、写入和观察路径，不是把每个音频块直接变成同步 HTTP。
3. **业务工具：**把 Python 查询服务暴露为符合配置的 MCP / OpenAPI 工具；先验证 schema 与错误返回，再接入前台。框架现有入口说明见[前台 MCP](../../reference/frontend-mcp.zh.md)与[OpenAPI](../../reference/frontend-openapi.zh.md)。

这些是基于已存在扩展边界的学习方向，不是本次已部署的新服务。Python 不能直接实现一个由 Node 模块导入的 JavaScript 对象；跨进程 / 网络边界需要 Adapter。

## 7. 示例如何用于验证框架理解

| 示例 | 最适合观察的东西 |
| --- | --- |
| [智能座舱](../../../examples/smart-cockpit/README_ZH.md) | 领域服务事实源、前后台不同工具面、GCP 环境事件、A2A 后台 |
| [客服](../../../examples/customer-service/README_ZH.md) | 查询在前台，受约束业务操作经后台，批准与输入生命周期 |
| [X-Omni](../../../examples/x-omni/README_ZH.md) | 视觉输入、摄像头环境状态与可选 WebRTC |
| [AI Passport](../../../examples/ai-passport/README_ZH.md) | 嵌入式设备接入和中继边界 |
| [LightRAG](../../../examples/lightrag/README_ZH.md) | 外部知识服务替换 Provider |
| [VoiceMem](../../../examples/voicemem/README_ZH.md)、[Memcode](../../../examples/memcode/README_ZH.md) | 外部记忆与 Provider 适配 |

先选一个示例，画出“客户端 → Gateway → 前台工具 / 后台 → 业务服务”的链路，核对每条箭头的接口。示例有自己的演示范围、模型要求和评估方法；场景得分不能当成框架所有模型 / 部署的统一保证。

**读完检查：**你应该能决定“想把 Python RAG 接进来”与“想把整个 Python Agent 接进来”分别使用 Knowledge Provider 和 BackendPort，并解释为什么二者不是同一件事。
