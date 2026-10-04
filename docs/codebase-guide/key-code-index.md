# 关键代码索引

[返回伴读入口](README.md)

基线：`f6dd0e3703d58e4941159c1be89447f3fcb5063a`，分析日期 2026-10-03。以下行号从本地源码逐项匹配声明或调用分支取得，不由推测填写。符号链接固定到该提交；文件列可打开当前本地文件。

这是一份行为入口索引，不是全部文件清单。先按职责选一组，再沿调用者与状态变化读。所有条目的定位依据为 **static**；已运行测试与未运行入口分别见[运行与测试](operations/runtime-and-tests.md)。

## 启动与应用装配

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [CLI executable](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/cli/bin/qwenaudio.mjs#L1) | [cli/bin/qwenaudio.mjs](../../cli/bin/qwenaudio.mjs)，L1 | 命令行可执行入口 |
| [main](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/cli/src/launcher.mjs#L220) | [cli/src/launcher.mjs](../../cli/src/launcher.mjs)，L220 | 命令分派与启动管理 |
| [Gateway process entry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/index.mjs#L1) | [server/src/index.mjs](../../server/src/index.mjs)，L1 | 环境、租约、后台与退出生命周期 |
| [bootstrap module](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/bootstrap.mjs#L1) | [server/src/app/bootstrap.mjs](../../server/src/app/bootstrap.mjs)，L1 | 创建默认应用并导出服务 |
| [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63) | [server/src/app/gateway-application.mjs](../../server/src/app/gateway-application.mjs)，L63 | 核心装配与依赖注入 |
| [registerGatewayHttpRoutes](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-http-routes.mjs#L30) | [server/src/app/gateway-http-routes.mjs](../../server/src/app/gateway-http-routes.mjs)，L30 | 控制面 HTTP 注册 |
| [createFrontendRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/frontend-runtime.mjs#L12) | [server/src/app/frontend-runtime.mjs](../../server/src/app/frontend-runtime.mjs)，L12 | 共享依赖和每连接 Session 创建 |
| [optionalModuleFactories](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/optional-modules.mjs#L6) | [server/src/app/optional-modules.mjs](../../server/src/app/optional-modules.mjs)，L6 | 应用级可选领域装配 |
| [optionalFrontendFeatures](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/optional-features.mjs#L6) | [server/src/frontend/optional-features.mjs](../../server/src/frontend/optional-features.mjs)，L6 | 前台可选能力装配 |
| [config](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/core/config.mjs#L234) | [server/src/core/config.mjs](../../server/src/core/config.mjs)，L234 | 解析后的产品配置 |
| [resolveRuntimePaths](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/runtime-paths.mjs#L19) | [shared/runtime-paths.mjs](../../shared/runtime-paths.mjs)，L19 | 配置、数据与状态路径策略 |
| [loadRuntimeEnvironment](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/runtime-environment.mjs#L254) | [shared/runtime-environment.mjs](../../shared/runtime-environment.mjs)，L254 | 加载配置、初始化模板与运行目录 |

## 客户端接入与实时会话

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62) | [server/src/transport/gateway-client-transport.mjs](../../server/src/transport/gateway-client-transport.mjs)，L62 | 接入、归属、协议路由与投影 |
| [createRealtimeSessionRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-session-runtime.mjs#L56) | [server/src/voice/realtime-session-runtime.mjs](../../server/src/voice/realtime-session-runtime.mjs)，L56 | 模型、音频、工具与播放生命周期 |
| [handleEvent: function_call_arguments.done](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-session-runtime.mjs#L575) | [server/src/voice/realtime-session-runtime.mjs](../../server/src/voice/realtime-session-runtime.mjs)，L575 | 模型工具调用进入真实 handler 的分支 |
| [RealtimeInputRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-input-runtime.mjs#L30) | [server/src/voice/realtime-input-runtime.mjs](../../server/src/voice/realtime-input-runtime.mjs)，L30 | 输入、语音轮次与提交 |
| [RealtimeFrontend](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-provider.mjs#L111) | [server/src/voice/realtime-provider.mjs](../../server/src/voice/realtime-provider.mjs)，L111 | 通用模型会话门面 |
| [RealtimeProviderRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/providers/provider-registry.mjs#L261) | [server/src/voice/providers/provider-registry.mjs](../../server/src/voice/providers/provider-registry.mjs)，L261 | 可替换实时 Provider 注册与校验 |
| [GATEWAY_CLIENT_PROTOCOL_VERSION / protocol definitions](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/protocol/gateway-client-protocol.mjs#L13) | [shared/protocol/gateway-client-protocol.mjs](../../shared/protocol/gateway-client-protocol.mjs)，L13 | 线版本、事件、能力和 schema |
| [GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63) | [shared/gateway/client-sdk.mjs](../../shared/gateway/client-sdk.mjs)，L63 | 握手、请求关联、重连与客户端生命周期 |
| [reduceGatewayClientState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-state.mjs#L29) | [shared/gateway/client-state.mjs](../../shared/gateway/client-state.mjs)，L29 | 客户端通用状态投影 |
| [GatewayClientCommandRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/client/client-command-runtime.mjs#L39) | [server/src/client/client-command-runtime.mjs](../../server/src/client/client-command-runtime.mjs)，L39 | 公开客户端命令与共用用户 Task 操作 |
| [GatewayAccessManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/access/gateway-access.mjs#L245) | [server/src/access/gateway-access.mjs](../../server/src/access/gateway-access.mjs)，L245 | 可信接入身份与凭据验证 |

## 前台工具与受理

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [frontendTools](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/frontend-tools.mjs#L109) | [server/src/frontend/frontend-tools.mjs](../../server/src/frontend/frontend-tools.mjs)，L109 | 组装当前模型可用工具 |
| [FrontendToolRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-registry.mjs#L107) | [server/src/frontend/tools/frontend-tool-registry.mjs](../../server/src/frontend/tools/frontend-tool-registry.mjs)，L107 | 定义登记、策略与可用性 |
| [FrontendToolExecutor](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-registry.mjs#L166) | [server/src/frontend/tools/frontend-tool-registry.mjs](../../server/src/frontend/tools/frontend-tool-registry.mjs)，L166 | 精确 handler 分派、能力与循环限制 |
| [assertFrontendToolSource](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-source.mjs#L12) | [server/src/frontend/tools/frontend-tool-source.mjs](../../server/src/frontend/tools/frontend-tool-source.mjs)，L12 | 动态工具来源契约 |
| [ToolCallHandler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/tool-call-handler.mjs#L78) | [server/src/frontend/tools/tool-call-handler.mjs](../../server/src/frontend/tools/tool-call-handler.mjs)，L78 | 模型调用关联、参数、工具输出和各 handler 装配 |
| [ToolCallHandler.handle](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/tool-call-handler.mjs#L481) | [server/src/frontend/tools/tool-call-handler.mjs](../../server/src/frontend/tools/tool-call-handler.mjs)，L481 | 真实模型事件入口 |
| [ToolCallHandler.sendOutput](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/tool-call-handler.mjs#L266) | [server/src/frontend/tools/tool-call-handler.mjs](../../server/src/frontend/tools/tool-call-handler.mjs)，L266 | 工具结果回送模型与续答 |
| [spawnThinkingTool](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/spawn-thinking-tool.mjs#L3) | [server/src/frontend/tools/spawn-thinking-tool.mjs](../../server/src/frontend/tools/spawn-thinking-tool.mjs)，L3 | 后台请求 schema 与语义边界 |
| [AgentTaskRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L60) | [server/src/frontend/tools/agent-task-runtime.mjs](../../server/src/frontend/tools/agent-task-runtime.mjs)，L60 | 受理、查询、取消、权限与输入工具 |
| [AgentTaskRuntime.executeSpawnThinkingToolCall](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L195) | [server/src/frontend/tools/agent-task-runtime.mjs](../../server/src/frontend/tools/agent-task-runtime.mjs)，L195 | 受理回执、输入、重复请求与可用性 |
| [agentTaskToolEntries](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/features/agent-task-tools.mjs#L119) | [server/src/frontend/tools/features/agent-task-tools.mjs](../../server/src/frontend/tools/features/agent-task-tools.mjs)，L119 | 任务工具 schema 与能力策略 |
| [InputAssetRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/input-asset-registry.mjs#L41) | [server/src/voice/input-asset-registry.mjs](../../server/src/voice/input-asset-registry.mjs)，L41 | 图片和文件历史引用及归属 |

## Task 状态、执行与权限

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [TaskOperations](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L34) | [server/src/orchestration/task-operations.mjs](../../server/src/orchestration/task-operations.mjs)，L34 | 传输中立的用户工作操作门面 |
| [TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57) | [server/src/orchestration/task-operations.mjs](../../server/src/orchestration/task-operations.mjs)，L57 | owner lane、runner 与 canceler 装配 |
| [TaskManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L56) | [server/src/task/task-manager.mjs](../../server/src/task/task-manager.mjs)，L56 | Task 状态、调度与通知权威 |
| [TaskManager.create / #create](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L428) | [server/src/task/task-manager.mjs](../../server/src/task/task-manager.mjs)，L428 | 工作受理并立即返回公开快照 |
| [TaskManager.drain](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L610) | [server/src/task/task-manager.mjs](../../server/src/task/task-manager.mjs)，L610 | 排序与调度配额选择 |
| [TaskManager.start](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L623) | [server/src/task/task-manager.mjs](../../server/src/task/task-manager.mjs)，L623 | 运行、后台事件、委派让出通道与终态 |
| [TaskManager.cancel](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L855) | [server/src/task/task-manager.mjs](../../server/src/task/task-manager.mjs)，L855 | 排队与已启动工作的确认式取消 |
| [TaskStatus / TRANSITIONS](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-state.mjs#L5) | [server/src/task/task-state.mjs](../../server/src/task/task-state.mjs)，L5 | 内部状态和允许转换 |
| [transitionTask](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-state.mjs#L131) | [server/src/task/task-state.mjs](../../server/src/task/task-state.mjs)，L131 | 非法转换保护 |
| [publicWorkState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-state.mjs#L117) | [server/src/task/task-state.mjs](../../server/src/task/task-state.mjs)，L117 | 权限 / 输入要求的公开投影 |
| [PermissionPolicy](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/permission-policy.mjs#L9) | [server/src/task/permission-policy.mjs](../../server/src/task/permission-policy.mjs)，L9 | 工作与会话范围的授权策略 |
| [normalizeArtifacts](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-artifact.mjs#L117) | [server/src/task/task-artifact.mjs](../../server/src/task/task-artifact.mjs)，L117 | 有界、公开的工作产物 |
| [ReminderScheduler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/reminder-scheduler.mjs#L24) | [server/src/task/reminder-scheduler.mjs](../../server/src/task/reminder-scheduler.mjs)，L24 | 定时提醒恢复与到期调度 |
| [taskRecoveryAction](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-recovery.mjs#L21) | [server/src/task/task-recovery.mjs](../../server/src/task/task-recovery.mjs)，L21 | 恢复、重排、重新关联、取消或失败策略 |

## 后台协议与进程

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [BACKEND_PORT_METHODS / assertBackendPort](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/backend-port.mjs#L22) | [server/src/backend/backend-port.mjs](../../server/src/backend/backend-port.mjs)，L22 | 协议中立接口契约 |
| [BackendWorkRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/backend-work-runtime.mjs#L14) | [server/src/backend/backend-work-runtime.mjs](../../server/src/backend/backend-work-runtime.mjs)，L14 | 构成执行输入并调用 BackendPort |
| [AcpBackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/acp/backend-adapter.mjs#L115) | [server/src/backend/adapters/acp/backend-adapter.mjs](../../server/src/backend/adapters/acp/backend-adapter.mjs)，L115 | ACP Session、委派、权限和恢复边界 |
| [AcpBackendAdapter.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/acp/backend-adapter.mjs#L1160) | [server/src/backend/adapters/acp/backend-adapter.mjs](../../server/src/backend/adapters/acp/backend-adapter.mjs)，L1160 | 真正后台工作入口及隔离工作分支 |
| [A2ABackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/a2a/backend-adapter.mjs#L513) | [server/src/backend/adapters/a2a/backend-adapter.mjs](../../server/src/backend/adapters/a2a/backend-adapter.mjs)，L513 | A2A 状态、输入和产物归一化 |
| [startManagedBackend](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/process/managed-backend.mjs#L181) | [server/src/process/managed-backend.mjs](../../server/src/process/managed-backend.mjs)，L181 | 本机后台进程启动和归属 |

## 结果投递与播放

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12) | [server/src/orchestration/session-task-coordinator.mjs](../../server/src/orchestration/session-task-coordinator.mjs)，L12 | 观察 Task、请求投递、通知领取和关闭 |
| [TaskNotificationQueue](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-notification-queue.mjs#L8) | [server/src/task/task-notification-queue.mjs](../../server/src/task/task-notification-queue.mjs)，L8 | claim、续期、释放和交付 |
| [AnnouncementWindow](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-window.mjs#L1) | [server/src/voice/announcement/announcement-window.mjs](../../server/src/voice/announcement/announcement-window.mjs)，L1 | 双工插入窗口 |
| [AnnouncementManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-manager.mjs#L66) | [server/src/voice/announcement/announcement-manager.mjs](../../server/src/voice/announcement/announcement-manager.mjs)，L66 | 批次、恢复、重试与播放确认 |
| [AnnouncementManager.deliver](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-manager.mjs#L351) | [server/src/voice/announcement/announcement-manager.mjs](../../server/src/voice/announcement/announcement-manager.mjs)，L351 | 请求模型表达并等待真正播放 |
| [confirmTrackedPlaybackStart](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/playback-lifecycle.js#L10) | [web/src/realtime/playback-lifecycle.js](../../web/src/realtime/playback-lifecycle.js)，L10 | Web 客户端确认实际开始播放 |
| [RealtimePresentationRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-presentation-runtime.mjs#L62) | [server/src/voice/realtime-presentation-runtime.mjs](../../server/src/voice/realtime-presentation-runtime.mjs)，L62 | 音频 / 文字呈现、通知确认与播放事实 |
| [RealtimePresentationRuntime.cancelPlayback](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-presentation-runtime.mjs#L608) | [server/src/voice/realtime-presentation-runtime.mjs](../../server/src/voice/realtime-presentation-runtime.mjs)，L608 | 主动打断的通知确认及迟到输出抑制 |

## 上下文、可选领域与持久化

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [buildFrontendContext](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/conversation/frontend-agent-context.mjs#L120) | [server/src/conversation/frontend-agent-context.mjs](../../server/src/conversation/frontend-agent-context.mjs)，L120 | 前台上下文与客户端环境 |
| [FrontendNotesStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/conversation/frontend-notes.mjs#L85) | [server/src/conversation/frontend-notes.mjs](../../server/src/conversation/frontend-notes.mjs)，L85 | 命名清单及跨进程持久集合 |
| [assertMemoryProvider / provider contract](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/provider.mjs#L76) | [server/src/memory/provider.mjs](../../server/src/memory/provider.mjs)，L76 | 同步快照与可选观察接口 |
| [FrontendMemoryRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/runtime.mjs#L53) | [server/src/memory/runtime.mjs](../../server/src/memory/runtime.mjs)，L53 | 归一化、变更与 owner 写入通道 |
| [buildMemoryContext](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/context.mjs#L60) | [server/src/memory/context.mjs](../../server/src/memory/context.mjs)，L60 | 偏好和事实的上下文边界 |
| [createMemoryModule](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/module.mjs#L10) | [server/src/memory/module.mjs](../../server/src/memory/module.mjs)，L10 | 记忆 Provider、学习、观察和路由装配 |
| [memoryToolHandlers](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/tools.mjs#L186) | [server/src/memory/tools.mjs](../../server/src/memory/tools.mjs)，L186 | read / append / replace 的模型工具入口 |
| [MemoryExtractor](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/learning/extractor.mjs#L202) | [server/src/memory/learning/extractor.mjs](../../server/src/memory/learning/extractor.mjs)，L202 | 会话后明确偏好与事实提取 |
| [assertKnowledgeRetrievalProvider](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/provider.mjs#L156) | [server/src/knowledge/provider.mjs](../../server/src/knowledge/provider.mjs)，L156 | 检索和可选管理契约 |
| [FrontendKnowledgeRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/runtime.mjs#L25) | [server/src/knowledge/runtime.mjs](../../server/src/knowledge/runtime.mjs)，L25 | 可信 owner、限量、超时和结果归一化 |
| [createKnowledgeModule](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/module.mjs#L9) | [server/src/knowledge/module.mjs](../../server/src/knowledge/module.mjs)，L9 | 知识 Provider、入库与路由装配 |
| [KnowledgeLibraryService](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/library-service.mjs#L20) | [server/src/knowledge/library-service.mjs](../../server/src/knowledge/library-service.mjs)，L20 | 异步资料入库与管理 |
| [LocalKnowledgeProvider](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/providers/local/provider.mjs#L104) | [server/src/knowledge/providers/local/provider.mjs](../../server/src/knowledge/providers/local/provider.mjs)，L104 | 确定性文本片段检索与本机管理 |
| [TaskStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-store.mjs#L17) | [server/src/task/task-store.mjs](../../server/src/task/task-store.mjs)，L17 | 工作快照与有序持久写入 |
| [SessionJournal](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal.mjs#L18) | [server/src/session/session-journal.mjs](../../server/src/session/session-journal.mjs)，L18 | 持久会话事件、写队列与压缩 |
| [SessionJournalRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal-registry.mjs#L17) | [server/src/session/session-journal-registry.mjs](../../server/src/session/session-journal-registry.mjs)，L17 | owner/session 的日志文件和缓存管理 |

## 客户端与音频实现

| 符号 / 入口 | 本地位置 | 为什么看它 |
| --- | --- | --- |
| [useRealtimeVoice](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/useRealtimeVoice.js#L203) | [web/src/realtime/useRealtimeVoice.js](../../web/src/realtime/useRealtimeVoice.js)，L203 | Web 的连接、采集、播放与交互 |
| [createStreamingResampler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/audio.js#L23) | [web/src/realtime/audio.js](../../web/src/realtime/audio.js)，L23 | 跨分块重采样状态 |
| [startConfiguredRuntime / Electron main](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/desktop/src/main.mjs#L390) | [desktop/src/main.mjs](../../desktop/src/main.mjs)，L390 | 桌面连接与内置运行时启动 |
| [DesktopWakeWordRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/desktop/src/wake-word/runtime.mjs#L3) | [desktop/src/wake-word/runtime.mjs](../../desktop/src/wake-word/runtime.mjs)，L3 | 客户端本地 Worker 唤醒检测 |
| [runTui](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/tui/src/index.mjs#L141) | [tui/src/index.mjs](../../tui/src/index.mjs)，L141 | 终端交互和音频客户端入口 |

## 更新时怎么处理行号

代码升级后，先查看相关功能 diff，再搜索这里列出的符号。旧基线链接仍描述旧快照；本地文件可能已经变化，不能只把 SHA 改成新值而保留旧行号。每个主张也应重新核对调用点与分支。

例如从模型到受理，搜索 `response.function_call_arguments.done` → `ToolCallHandler.handle` → `executeSpawnThinkingToolCall` → `TaskOperations.submit` → `TaskManager.create`；从完成到播放，搜索 `SessionTaskCoordinator` → `AnnouncementManager.deliver` → `playback.started`。
