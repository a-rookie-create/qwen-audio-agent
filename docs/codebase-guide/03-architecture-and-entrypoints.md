# 第 2 讲：架构怎样落到代码与启动入口

[讲义入口](README.md) · 上一讲：[整体架构](00-system-overview.md) · 下一讲：[实时对话与工具](flows/voice-and-tools.md)

带着上一讲的角色地图，本讲回答：**它们在哪些目录里实现，谁把它们连接起来？**

## 1. 先读原文，再打开三个代码入口

| 顺序 | 原文 | 本次关注 |
| --- | --- | --- |
| 1 | [服务端源码导航](../../server/src/README.md) | 目录职责表；“前台会话与传输”；“任务协调” |
| 2 | [详细架构：依赖方向](../architecture/deep-dive.zh.md#9-依赖方向) | 什么属于通用运行时，什么留在 Provider / Adapter；组合根如何接线 |
| 3 | [Gateway 运行](../operations/gateway.zh.md#从源码启动)与[Gateway 契约](../contract.zh.md#嵌入流程) | 现成 CLI 启动和代码嵌入是怎样的两种入口 |

目录的完整职责表直接看源码导航；公开包入口直接看[契约“包入口”](../contract.zh.md#包入口package-exports)。内部文件路径用于理解实现，开发扩展时使用公开导出。

## 2. 讲义补充：从 Python 的应用工厂理解组合根

想象一个 Python `create_app()`：它先创建存储、任务服务和外部服务客户端，再把对象作为参数交给请求处理器。这就是本项目原文所说的 **Composition Root / 组合根**。它的主要工作是选实现、创建对象、连接依赖和安排关闭。

因此第一次打开 [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)，先看参数和 `new` / 工厂调用：

1. 哪些对象可以从参数注入，哪些在缺省时创建？
2. `TaskManager` 与 `TaskOperations` 怎样连接？
3. 同一个 `taskOperations` 被交给了哪些入口？
4. 模型、记忆、知识和工具的实现在哪里被选择？

这里的 JS 参数对象可类比 Python 的配置字典；默认值、解构和展开见[语言桥梁第 3 节](01-python-to-javascript.md#3-对象解构与展开读懂配置和依赖注入)。参数传递让调用方能换实现；业务模块不用自行猜测供应商。

## 3. 把“启动”“装配”“使用”接起来

CLI 启动路径的定位顺序是：[命令入口](../../cli/bin/qwenaudio.mjs) → [launcher 的 main](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/cli/src/launcher.mjs#L220) → [服务进程入口](../../server/src/index.mjs) → [bootstrap](../../server/src/app/bootstrap.mjs) → `createGatewayApplication`。这是 **static 源码定位**，用来把原文运行命令对应到代码；配置、诊断等命令有自己的分支。

装配之后，再看两处：

| 代码定位 | 带着什么问题看 |
| --- | --- |
| [createFrontendRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/frontend-runtime.mjs#L12) | 哪些依赖共享，`createSession()` 每次创建什么？ |
| [attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62) | 接入通过后，如何把解码事件交给前台运行时？ |

对照[原文“前台会话与传输”](../../server/src/README.md)。Python 中也常把 Socket 处理和业务对象分开：网络入口处理连接，业务对象接收已验证的参数。这里传输层与前台会话运行时的分工同样需要分开理解。

## 4. 讲义补充：对象生命周期决定哪些状态能共享

一个 Python 模块里的单例、每个请求创建的对象、每次循环的局部变量，生命周期不同。本项目应区分应用级服务、连接级会话和单次操作。原文的每连接 `SessionTaskCoordinator` 与共用 Task 服务，正是这种差别。

特别留意：**共享任务管理服务，不代表共享一个模型会话。** 重连可能创建新的前台运行实例，已受理工作仍由应用级任务服务管理。回到[源码导航](../../server/src/README.md)的关闭说明，看关闭连接释放了什么，再在下一讲追一次输入。

可选模块的装配也有原文：[裁剪可选模块](../../server/src/README.md)及[依赖方向](../architecture/deep-dive.zh.md#9-依赖方向)。这里的两处显式接线可类比 Python 的 `create_app()` 注册模块；不要把它理解成任意目录可动态发现和删除。

## 5. 本讲检查题

1. `app/` 为什么可以选择具体 Provider，而通用业务模块要依赖接口？
2. 同一个 TaskOperations 被交给前台工具和客户端命令，有什么作用？
3. 每个连接创建独立会话后，哪些任务事实仍然共享？
4. 代码里用 `import` 打开 bootstrap，是否可能立即执行装配？

前三题回源码导航与装配入口；第四题回[语言桥梁“模块执行”](01-python-to-javascript.md#2-导入导出与模块执行)。更多定位按需查[代码索引](key-code-index.md)。
