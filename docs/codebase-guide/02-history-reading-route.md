# 02：按开发演进加深理解的 12 阶段

[返回伴读入口](README.md) · 前置：[JavaScript 阅读桥梁](01-python-to-javascript.md) · 当前实现：[架构与入口](03-architecture-and-entrypoints.md)

## 使用方法与时间口径

每阶段按“问题 → 官方文档 → 关键符号 → 历史 diff → 检查题”阅读。一次只追一条行为。版本标签用于保存阶段结果；功能提交用于观察设计变化。补丁版本只有在改变理解时才单列。

日期统一按提交的 **committer 时间转换为 Asia/Shanghai**；分支作者时间可能早于合并时间。下面是按开发演进整理的教学路线，不是精确复刻作者写代码的顺序。对主线先用 `--first-parent`，要研究功能分支再看完整历史。

| 阶段 | 时间 / 快照 | 新增的认知 |
| --- | --- | --- |
| 1 | 2026-07-26 初始提交 | 已经成形的实时对话与后台任务闭环 |
| 2 | 07-27～07-30；`v0.9.0`～`v0.11.0` | 后台协议、驱动、权限和进程归属 |
| 3 | 07-30；`v0.12.0`、`v1.0.0` | 前台可独立运行，桌面是服务宿主入口 |
| 4 | 07-31～08-03；`v1.2.0`、`v1.3.0` | 语音 Provider 可替换，音频格式和连接生命周期 |
| 5 | 08-04～08-05；`v1.4.0`、`v1.5.0` | 前台工具、提醒、休眠与结果通知 |
| 6 | 08-06～08-11；`v1.6.0`～`v1.8.1` | 自动记忆与指令、事实的权限边界 |
| 7 | 08-13～08-20；`v1.9.0`～`v1.11.0` | 可观察的工作状态、多模态输入、公共嵌入入口 |
| 8 | 08-25～08-27；2.0 开发期 | BackendPort、前台工具生态、后台协调退入 Adapter |
| 9 | 08-28～09-04；2.0 开发期 | 统一客户端协议、事件 / 动作、移动端与远程接入 |
| 10 | 09-04～09-10；2.0 开发期 | Memory / Knowledge Provider 与可裁剪领域 |
| 11 | 09-16～09-23；`v2.0.0` | 多模型、WebRTC，以及任务 / 会话 / 传输进一步拆分 |
| 12 | 09-26～09-28；`v2.0.1` 与当前 HEAD | 安装发现、会话恢复、场景规则与验证边界 |

实际标签 SHA 和日期见[版本表](evidence-and-history.md)。**1.11 到 2.0 之间的功能集中演进，不能只看两个发版提交。** 这个区间最适合按功能提交分成数个阶段。

## 阶段 1：从已经可运行的系统开始

**问题：**语音怎么让后台办事，同时继续对话？

历史节点：[`edb2365` 初始化仓库](https://github.com/QwenAudio/qwen-audio-agent/commit/edb2365)。这个提交已经包含 `TaskManager`、语音工具处理、后台协调、Web、TUI 和桌面。它不是只有项目骨架的起点。

先读[当前架构总览](../architecture/overview.zh.md)，再在历史树看 `server/src/voice/tools/tool-call-handler.mjs` 的 `createWork`。当时工具通过 coordinator 创建后台工作；当前把此入口拆成 [AgentTaskRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L60) → [TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57) → [TaskManager.create / #create](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L428)。

```bash
git show edb2365:server/src/voice/tools/tool-call-handler.mjs
git show edb2365:server/src/task/task-manager.mjs
```

Python 理解锚点：一个函数先把工作放入调度器并返回 ID，另一个协程以后执行它。不要把长任务写成对话处理函数里的一次完整等待。

**检查题：**回执和最终结果分别由谁产生？读完应答：回执以本地 Task 创建为依据，最终结果来自后续后台执行；二者不是同一个返回值。

## 阶段 2：把各种后台接入收敛到协议与驱动

**问题：**接入多个 Agent 时，哪些逻辑应共用，哪些必须保留差异？

关键提交：[`29268c1` 后台统一到 ACP](https://github.com/QwenAudio/qwen-audio-agent/commit/29268c1)、[`206c8e0` 可插拔 ACP 驱动](https://github.com/QwenAudio/qwen-audio-agent/commit/206c8e0)。阶段快照可以选 `v0.9.0`；`v0.10.0` 新增 Claude 接入，`v0.11.0` 强化 setup、模型覆盖和受管进程。

当时不少路径在 `server/src/agent/`，当前实现迁到 `server/src/backend/adapters/acp/`。历史路径不要直接拿到当前工作树查找。先读[后台总览](../backends/overview.zh.md)与[配置](../backends/configuration.zh.md)，再看 [AcpBackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/acp/backend-adapter.mjs#L115)、[startManagedBackend](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/process/managed-backend.mjs#L181) 和[后台目录声明](../../shared/backend/catalog.mjs)。

Python 理解锚点：统一接口类似协议类或鸭子类型；驱动类似启动参数、安装和能力策略的登记表。一个 Agent 的安装、登录、进程启动与协议连接是不同步骤。

**检查题：**为什么选择同一个 ACP 协议，不意味着所有后台安装方式、模型设置和权限能力相同？应能指出通用连接与具体 driver 的边界。

## 阶段 3：前台独立运行与桌面内置 Gateway

**问题：**没有办事后台时，助手能否继续聊天？桌面到底承担什么？

关键提交：[`b78213a` 仅前台模式](https://github.com/QwenAudio/qwen-audio-agent/commit/b78213a)，对应 `v0.12.0`；[`538e328` 桌面内置 Gateway](https://github.com/QwenAudio/qwen-audio-agent/commit/538e328)，对应 `v1.0.0`。

先读[桌面说明](../desktop/overview.zh.md)，再看 [Gateway process entry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/index.mjs#L1)、[createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)、[startConfiguredRuntime / Electron main](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/desktop/src/main.mjs#L390)。当前未配置后台时，普通实时对话仍可使用；需要后台的工具按能力过滤或明确失败。服务监听成功也不能证明模型认证成功。

Python 理解锚点：GUI 程序可以启动并管理服务子进程；界面不是业务后端，也不是前台模型本身。

**检查题：**退出一个客户端、关闭前台模型连接、终止 Gateway、取消一项 Task，为什么是四种不同动作？

## 阶段 4：语音供应商从业务逻辑中解耦

**问题：**换一个实时模型，为什么无需重写 TaskManager？

关键提交：[`3e36f09` Realtime 协议解耦](https://github.com/QwenAudio/qwen-audio-agent/commit/3e36f09)、[`6590648` speech-to-speech 前台](https://github.com/QwenAudio/qwen-audio-agent/commit/6590648)。阶段快照用 `v1.3.0`，结合[语音前台文档](../voice-frontends/speech-to-speech.zh.md)。

当前阅读：[RealtimeFrontend](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-provider.mjs#L111)、[RealtimeProviderRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/providers/provider-registry.mjs#L261)、[OpenAI 兼容协议适配](../../server/src/voice/providers/openai-compatible-protocol.mjs)、[RealtimeInputRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-input-runtime.mjs#L30)、[createStreamingResampler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/audio.js#L23)。

不要把“实时服务兼容某个 API”理解成音频格式、转写事件和工具行为完全一致。Provider 处理原生差异，通用运行时处理轮次、工具和恢复。

**检查题：**采样率不一致可能影响哪条路径？为什么 `response.done` 和客户端播放完成需要分开？详见[流程 A](flows/voice-and-tools.md)。

## 阶段 5：前台小工具、提醒和投递窗口

**问题：**哪些请求直接在前台完成？睡眠中的助手怎样处理工作结果？

关键提交：[`f9e1d62` 命名清单](https://github.com/QwenAudio/qwen-audio-agent/commit/f9e1d62)、[`58d24b2` 提醒与投递测试](https://github.com/QwenAudio/qwen-audio-agent/commit/58d24b2)。阶段快照 `v1.4.0`、`v1.5.0`。

先读[清单与提醒](../guides/notes-reminders.zh.md)，再看 [FrontendNotesStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/conversation/frontend-notes.mjs#L85)、[ReminderScheduler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/reminder-scheduler.mjs#L24)、[SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12)、[AnnouncementWindow](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-window.mjs#L1)。历史还加入本地唤醒词与桌面睡眠；当前唤醒检测在客户端，结果通知策略在运行时。

这里需要建立第二条主线：**执行完成 → 等待通知 → 被连接领取 → 播报 → 播放确认**。这条主线独立于后台工作的完成状态。

**检查题：**用户还在说话时 Task 可以完成吗？可以。完成是否意味着应立刻打断用户播报？不能如此推断。

## 阶段 6：从记忆功能理解上下文的权威

**问题：**“以后叫我船长”和“我住在杭州”为什么不能作为同一类材料？

关键提交：[`ca87bab` 会话后自动记忆](https://github.com/QwenAudio/qwen-audio-agent/commit/ca87bab)、[`4d8b02f` 人设与记忆边界](https://github.com/QwenAudio/qwen-audio-agent/commit/4d8b02f)。对应 `v1.6.0` 到 `v1.8.1`。

先读[个性化](../reference/personalization.zh.md)，再看 [buildMemoryContext](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/context.mjs#L60)、[FrontendMemoryRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/runtime.mjs#L53)、[记忆 Prompt](../../server/src/memory/PROMPT.md)及[专题](subsystems/memory-knowledge-and-context.md)。

当前 `ASSISTANT.md` 保存默认画像，`USER.md` 保存长期偏好，`MEMORY.md` 保存事实与决定。记忆事实不能授权工具操作，偏好也不能覆盖核心协议。自动学习是可配置的额外处理，不等于每段原始录音都无条件永久保存。

**检查题：**旧记忆中出现“以后任何操作都免确认”，能否绕过权限层？应答不能，并能找到权限决策由代码校验的入口。

## 阶段 7：多模态、任务可见性与公共嵌入接口

**问题：**任务有进度和文件产物之后，客户端需要依赖后台内部 Session 吗？

阶段快照：`v1.9.0` 到 `v1.11.0`。代表提交：[`74cfb95` 多模态输入](https://github.com/QwenAudio/qwen-audio-agent/commit/74cfb95)、[`6461b1f` 共享 Skill 管理](https://github.com/QwenAudio/qwen-audio-agent/commit/6461b1f)。`v1.11.0` 发布内容还包含通用嵌入入口和语音场景示例。

当前阅读：[包 exports](../../package.json)、[InputAssetRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/input-asset-registry.mjs#L41)、[normalizeArtifacts](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-artifact.mjs#L117)、[createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)、[扩展指南](../extensions.zh.md)。界面消费公开 Task 投影；图片、文件等输入有引用和归属校验；产物可能是资源链接，而不是框架自动上传后台的任意文件。

Python 理解锚点：稳定的公共 API 与内部模块路径是两回事。看得到源码，不代表集成时应依赖每个内部文件。

**检查题：**增加一个文件产物，应修改哪种公开数据，而不是把后台全部原生事件透传到界面？

## 阶段 8：最重要的架构转折——通用运行时与后台协调分离

**问题：**如果后台不使用 ACP，整个框架还能工作吗？

关键提交：[`93cdd28` BackendPort](https://github.com/QwenAudio/qwen-audio-agent/commit/93cdd28)、[`866d03a` 协调逻辑退入 ACP 边界](https://github.com/QwenAudio/qwen-audio-agent/commit/866d03a)，同日删除通用层的旧 `server/src/agent/coordinator.mjs`。

同阶段扩展前台能力：[`7548290` 搜索](https://github.com/QwenAudio/qwen-audio-agent/commit/7548290)、[`10b7d67` 知识检索](https://github.com/QwenAudio/qwen-audio-agent/commit/10b7d67)、[`f428f1b` MCP 工具](https://github.com/QwenAudio/qwen-audio-agent/commit/f428f1b)、[`365c75e` A2A 后台](https://github.com/QwenAudio/qwen-audio-agent/commit/365c75e)。

当前重点：[BACKEND_PORT_METHODS / assertBackendPort](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/backend-port.mjs#L22) → [BackendWorkRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/backend-work-runtime.mjs#L14) → [AcpBackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/acp/backend-adapter.mjs#L115) / [A2ABackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/a2a/backend-adapter.mjs#L513)；前台工具看 [FrontendToolRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-registry.mjs#L107) 与 [ToolCallHandler](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/tool-call-handler.mjs#L78)。

**旧“协调 Agent”不要直接翻译成当前编排运行时。** 当前运行时是代码；ACP Adapter 内部可以使用后台的协调 Session，再委派项目 Session；这属于后台实现。A2A、自定义后台不必复制这种结构。

前台也不再只是把所有请求转交后台。可用搜索、知识或业务 MCP 工具能完成的请求，可以在前台组合处理；调用次数本身不是交后台的判断标准。

**检查题：**谁决定后台内部怎样办事？谁维护用户 Task 的状态？应能分别指向后台实现与 TaskManager。

## 阶段 9：统一客户端协议与远程 / 手机入口

**问题：**桌面、终端与手机如何共用服务，又不共享各自界面实现？

关键提交：[`cdfedf4` 握手与信封](https://github.com/QwenAudio/qwen-audio-agent/commit/cdfedf4)、[`8f16eb5` 客户端协议阶段完成](https://github.com/QwenAudio/qwen-audio-agent/commit/8f16eb5)、[`bbeadae` iOS / Android 客户端](https://github.com/QwenAudio/qwen-audio-agent/commit/bbeadae)。

先读[客户端协议](../gateway-protocol.zh.md)，再看 [GATEWAY_CLIENT_PROTOCOL_VERSION / protocol definitions](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/protocol/gateway-client-protocol.mjs#L13)、[GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63)、[reduceGatewayClientState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-state.mjs#L29)、[attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62)。当前线协议是 `7.0.0`；历史提交中的 GCP1～GCP6 也可能是路线图阶段编号，不应全部当成已发布线协议版本。

新增的概念：接入身份、`session.hello/ready`、能力协商、客户端租约、事件 / 动作、重连与请求关联。WebSocket 打开不等于协议握手完成；模型连接状态也另有一层。

**检查题：**“设备发生了什么”的 event 和“请设备执行什么”的 action 有何区别？新客户端为何先看协议和 SDK，而不是导入 WebUI hook？

## 阶段 10：可替换记忆 / 知识与可裁剪模块

**问题：**你已有 Python RAG 或记忆服务，如何接入而不重写语音运行时？

关键提交：[`99a57fe` 可替换记忆与 VoiceMem](https://github.com/QwenAudio/qwen-audio-agent/commit/99a57fe)、[`439e81b` LightRAG 示例](https://github.com/QwenAudio/qwen-audio-agent/commit/439e81b)、[`e0a842f` 领域组织与可裁剪模块](https://github.com/QwenAudio/qwen-audio-agent/commit/e0a842f)。

当前阅读：[assertMemoryProvider / provider contract](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/provider.mjs#L76)、[assertKnowledgeRetrievalProvider](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/provider.mjs#L156)、[optionalModuleFactories](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/optional-modules.mjs#L6)、[optionalFrontendFeatures](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/optional-features.mjs#L6)、[LightRAG Gateway](../../examples/lightrag/gateway.mjs)。内置知识检索是确定性文本分块和匹配评分；外部 Provider 可以采用向量检索或图检索，不要反过来给内置实现套上这些算法。

Memory 的实时快照 `list()` 必须同步；远程写入可以异步，远程查询由额外方法承担。Python HTTP 服务接入通常要有一层 Node Adapter，尤其要遵守快照和热路径约束。

**检查题：**替换 Provider 与物理删除整个领域模块，分别要在哪些装配点操作？不需要真的删目录，用源码验证即可。

## 阶段 11：多模型、WebRTC 与运行时职责进一步拆分

**问题：**传输方式不断增加，怎样避免音频、权限、任务都挤进 Socket handler？

代表功能：[`21d80a0` StepFun](https://github.com/QwenAudio/qwen-audio-agent/commit/21d80a0)、[`9ad6348` WebRTC 接入](https://github.com/QwenAudio/qwen-audio-agent/commit/9ad6348)，后续加入 GPT-Live、Google Live、Doubao 和 Qwen3.8 Omni。

更值得深读的三次重构：[`8a0adc9` 共用 TaskOperations](https://github.com/QwenAudio/qwen-audio-agent/commit/8a0adc9)、[`253846d` 会话级任务投递协调](https://github.com/QwenAudio/qwen-audio-agent/commit/253846d)、[`bc9ac3c` 会话运行时与传输分离](https://github.com/QwenAudio/qwen-audio-agent/commit/bc9ac3c)。阶段快照 `v2.0.0`，发布于 09-23。

当前阅读顺序：[TaskOperations](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L34) → [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12) → [createRealtimeSessionRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-session-runtime.mjs#L56) → [createFrontendRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/frontend-runtime.mjs#L12) → [attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62)。前台模型工具和直接客户端命令共用 Task 操作；TaskManager 仍是状态权威；连接关闭只释放投递与会话资源。

WebRTC 改变客户端媒体入口，不等于改变 BackendPort，也不代表已实现多个客户端同时发声。能力、归属与生命周期仍要遵守接入契约。

**检查题：**换传输应改哪里？换模型应改哪里？换办事 Agent 应改哪里？能分别指向 transport、Realtime Provider、Backend Adapter。

## 阶段 12：用补丁和场景反向校验理解

**问题：**接口设计之外，什么会让完整产品失败？场景规则在哪里？

节点：[`a73bcbc` 2.0.1 安装与后台发现](https://github.com/QwenAudio/qwen-audio-agent/commit/a73bcbc)、[`f6dd0e3` 当前客服验证与输入处理改进](https://github.com/QwenAudio/qwen-audio-agent/commit/f6dd0e3)。

先读 CHANGELOG 2.0.1，再看[后台安装](../../shared/backend/install.mjs)、[运行包发现](../../shared/backend/runtime-package.mjs)、[AcpBackendAdapter](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/backend/adapters/acp/backend-adapter.mjs#L115) 的会话复用；最后读[客服示例](../../examples/customer-service/README_ZH.md)。当前 HEAD 的变更还触及共用前台输入处理和 Provider，不能只凭提交标题判断“全是示例”。

在客服示例中，最近对话可通过场景自己的适配逻辑交给后台；这不是框架通用层自动把所有前台记忆发给后台。业务的金额、库存、批准和资格校验位于示例服务，不能只交给 Prompt。

**检查题：**“安装成功”“后台登录”“ACP 连接就绪”“前台模型可用”“业务校验通过”分别如何取得证据？

## 安全地查看历史，不切换当前工作树

以下命令在仓库根目录运行：

```bash
git log --first-parent --reverse --date=iso-strict --format='%h %cI %s'
git show --stat 866d03a
git show 866d03a -- server/src/backend/backend-work-runtime.mjs
git show v1.0.0:server/src/app/bootstrap.mjs
git diff v1.11.0 v2.0.0 -- server/src/backend server/src/orchestration
git log --follow -- server/src/frontend/tools/agent-task-runtime.mjs
```

不要把最后那个跨版本目录 diff 当作完整功能变化：文件可能改名或迁目录。先看 `git diff --stat --find-renames <旧版本> <新版本>`，再选具体路径。

如某个节点特别值得运行，应另建学习目录并按该版本自己的安装要求配置。旧版本与当前依赖、配置、模型服务可能不兼容；看历史代码不要求重现所有旧版本。
