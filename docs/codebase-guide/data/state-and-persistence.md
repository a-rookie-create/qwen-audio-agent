# 状态与持久化：谁拥有事实，重启能恢复什么

[返回伴读入口](../README.md) · 关联：[Task 流程](../flows/tasks-permissions-and-delivery.md)

## 1. 先确定状态权威

| 状态 / 事实 | 权威与路径 | 其他模块如何使用 |
| --- | --- | --- |
| Task 生命周期、产物、通知 | TaskManager / TaskRepository / TaskStore | 公开快照、领域事件、查询和领取 |
| 是否允许当前操作 | PermissionPolicy + 真实后台请求 + 用户决定 | TaskOperations 转发并限制范围 |
| 模型连接、轮次、响应与播放窗口 | 前台 Session 的 voice 模块 | 控制回复、工具续答与安全播报 |
| 已记录的会话事件 | SessionJournal / Registry | 回放与恢复、投影 |
| 当前对话展示 | ConversationSync 与对话投影 | UI 历史、上下文组装 |
| 长期偏好与事实 | Memory Provider | 前台上下文、明确写入与可选学习 |
| 业务库存、退款资格等 | 示例领域服务 | 前后台工具调用共同访问 |

依据：[TaskManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L56)、[PermissionPolicy](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/permission-policy.mjs#L9)、[createRealtimeSessionRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-session-runtime.mjs#L56)、[SessionJournal](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal.mjs#L18)、[assertMemoryProvider / provider contract](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/provider.mjs#L76)。普通模型文本、UI 动画和日志中的一行说明，都不能取代这些权威。

## 2. 配置、数据和运行状态目录分开

[resolveRuntimePaths](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/runtime-paths.mjs#L19) 默认配置根为 `~/.config/qwaudio`（也支持 XDG 和显式覆盖）。`data/` 存用户持久数据，`state/` 或客户端 / Gateway 的状态目录存运行实例状态，`cache/` 存缓存。`QWAUDIO_CONFIG_DIR / DATA_DIR / STATE_DIR / CACHE_DIR / WORKSPACE` 可以覆盖相应位置。

下表是默认职责，最终解析结果仍要读运行环境与配置，而不能只凭目录名：

| 材料 | 典型位置 | 实现入口 |
| --- | --- | --- |
| 用户配置 | `<config-dir>/config.env` | shared/runtime-environment.mjs |
| 助手画像 | `<config-dir>/ASSISTANT.md` | runtime environment / frontend profile |
| 长期偏好、事实 | `<data-dir>/USER.md`、`MEMORY.md` | Markdown Memory Provider |
| 命名清单 | `<data-dir>/frontend-notes.json` | FrontendNotesStore |
| 工作快照 | `<state-dir>/tasks.json` | TaskStore |
| 会话事件日志 | `<state-dir>/sessions/` 下的会话文件 | SessionJournalRegistry |
| ACP Session 注册 | 默认 `<state-dir>/acp-sessions.json` | ACP Session Registry / config |
| 资料库 | 配置确定的本机 library 目录或外部服务 | Knowledge Module / Provider |
| 后台工作区 | 默认共享 workspace，或独立配置目录 | backend workspace 解析 |

依据：[loadRuntimeEnvironment](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/runtime-environment.mjs#L254)、[config](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/core/config.mjs#L234)、[TaskStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-store.mjs#L17)、[SessionJournalRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal-registry.mjs#L17)。旧版本曾采用更强的桌面 / CLI 数据隔离；当前共享配置与用户数据，同时隔离运行状态。不能把旧 CHANGELOG 的目录策略直接视为当前实现。

## 3. 快照和事件日志为什么同时存在

TaskRepository 管当前记录，TaskStore 存有版本号的 JSON 快照与编号状态。它处理文件缺失、格式损坏、隔离、警告及延迟进度写入。关键终态与异步进度写入之间有防止旧写覆盖新状态的逻辑。看 [TaskStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-store.mjs#L17)。

SessionJournal 追加规范化事件，使用事件 ID 处理重复，维护写队列、保留限制、压缩与文件损坏尾部处理。它不依赖 TaskManager / ACP，消费者再根据日志构建投影。看 [SessionJournal](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal.mjs#L18)、[保留策略](../../../server/src/session/session-journal-retention.mjs)。

应用装配把 Task 事件复制进日志，而不是让会话日志共享一个可变 Task 对象作为事实。看 [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63) 的 Task journal 订阅。事件回放也不等于重新执行所有命令；“重建状态”与“重做外部副作用”必须区分。

本次运行 `task-store.test.mjs`、`task-repository.test.mjs` 和 `session-journal.test.mjs`。这验证所选存储行为，不是任意磁盘故障或跨进程部署的全面证明。

## 4. 重启不是重新执行所有工作

[taskRecoveryAction](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-recovery.mjs#L21) 定义恢复策略，简化如下：

| 已保存情况 | 可能采取的恢复动作 |
| --- | --- |
| scheduled 或可重放的 reminder | 重新安排到期执行 |
| cancelling | 完成取消路径 |
| delegated / finalizing 且具备委派与 Session 关联 | 列为重新关联候选，再由后台恢复能力处理 |
| 其他仍 active 的普通工作 | 标为失败，避免盲目重做外部操作 |
| 终态记录 | 恢复记录与通知状态 |
| 通知原来 delivering | 可恢复为 pending，后续重新领取 |

恢复候选并不保证后台目标仍存在或 Adapter 一定恢复成功。通用策略与 Adapter 的恢复实现要一起看。前台重连则通常只是重新领取通知 / 投递未解决请求，不是 Gateway 进程重启，也不重跑已受理 Task。

## 5. 默认值还要经过装配配置

一个很有用的阅读例子：TaskManager 构造器里的 terminalTtlMs 默认是 3 天，但当前 `core/config.mjs` 的对应缺省值是 1 天，正常应用装配显式把 config 传进去。所以部署的保留时间不能只看类的默认值或旁边注释。

类似地，TaskManager 的 owner 并发配额，与 TaskOperations 后台 lane 的限制不同。所有配置要沿 **环境 / 配置解析 → 装配实参 → 对象实际行为** 核对。依据 [TaskManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L56)、[config](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/core/config.mjs#L234)、[createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)、[TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57)。

## 6. 不同“会话”不要混用

- 客户端逻辑 sessionId 是对话与操作归属的一部分。
- 前台 Session Runtime 属于一次连接的状态和资源，重连可创建新运行实例。
- SessionJournal 持有可回放的逻辑会话事件。
- ACP 协调 / 项目 Session 是后台原生执行上下文，标识保留在 Adapter 边界。
- A2A contextId / 原生 taskId 属于外部协议，Adapter 负责关联。

源码中同样出现 session 字样时，先问“谁创建、谁存、谁销毁、是否跨连接”，再决定它是否是同一概念。

**读完检查：**Gateway 重启后，一个正在写外部系统的 running Task 与一个 scheduled reminder 为什么不能无差别重跑？请从恢复策略找依据。
