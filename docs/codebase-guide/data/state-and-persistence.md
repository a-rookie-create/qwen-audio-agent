# 第 6 讲：状态、持久化与恢复

[讲义入口](../README.md) · 上一讲：[记忆与知识](../subsystems/memory-knowledge-and-context.md) · 下一讲：[客户端与扩展](../subsystems/clients-and-extensions.md)

本讲回答：**同一个用户的数据、一次对话、一项工作分别由谁保存？换连接或重启后能恢复什么？**

## 1. 先读原文的目录与会话说明

| 顺序 | 原文 | 本次关注 |
| --- | --- | --- |
| 1 | [配置总览](../../configuration.zh.md) | “配置优先级”“配置与数据目录”“客户端目录” |
| 2 | [基本概念](../../getting-started/concepts.zh.md) | “会话、工作与工作区”“本机与远程” |
| 3 | [Gateway 运行](../../operations/gateway.zh.md#实例与客户端) | 一个实例与多个客户端的区别，以及进程所有权 |
| 4 | [客户端协议：回放、错误与限制](../../gateway-protocol.zh.md#8-回放错误与限制)与[架构：Task 状态](../../architecture/deep-dive.zh.md#5-task-状态) | 恢复哪些事实，哪些工作无法安全恢复 |

具体目录和保留设置直接查原文。内部状态文件格式是否可以作为外部依赖，先看[Gateway 契约的开头](../../contract.zh.md)。

## 2. 讲义补充：文件存在不等于状态相同

你在 Python 中可能同时有配置文件、用户数据、当前进程状态和可重建缓存。它们都在磁盘上，生命周期仍然不同。把这个经验用于原文目录表：先问这个目录属于用户、Gateway 实例还是客户端，再问它是否可共享。

例如，桌面和 CLI 共享用户偏好，并不表示它们正在使用同一个 TaskManager。对照[配置目录表](../../configuration.zh.md#配置与数据目录)与[实例说明](../../operations/gateway.zh.md#实例与客户端)，解释为什么“看得到同一份记忆”与“看得到同一项工作”是两件事。

继续把[记忆回溯](../../reference/memory.zh.md#会话回溯)与[工作状态](../../guides/tasks.zh.md#看懂工作状态)放在一起读：摘要能帮助想起聊过什么，但当前执行事实仍需查任务台账。

## 3. 源码补充：快照与事件日志解决不同问题

原文提供目录和外部回放契约；内部存储实现可按下面的 **static 定位** 理解：

| 文件 / 符号 | 阅读问题 |
| --- | --- |
| [TaskStore](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-store.mjs#L17) | 当前任务记录怎样保存成快照？ |
| [SessionJournal](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/session/session-journal.mjs#L18) | 会话事件怎样追加、排序和恢复？ |
| [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63) | 谁将 Task 变化记录到会话日志？ |

Python 类比：一个 JSON 文件保存当前字典；另一份追加日志保存发生过的事件。读日志重建展示与状态，不代表再次执行造成外部副作用的函数。外部客户端依赖的回放行为读协议，内部文件实现读上述代码，两种边界不能混用。

## 4. 重连、重启与续接后台各指什么

重连是客户端连接发生变化；Gateway 重启是应用内存和资源重建；后台原生 Session 恢复是 Adapter 与执行服务的能力。按[基本概念](../../getting-started/concepts.zh.md)、[架构第 4、5、7 节](../../architecture/deep-dive.zh.md)和[A2A 会话连续性](../../reference/a2a-backend-adapter.zh.md#会话连续性)分别阅读。

想核对具体重启策略时看 [taskRecoveryAction](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-recovery.mjs#L21)：提醒可重新调度；取消中的工作走取消；有持久关联的委派工作可能重新挂接；其他活动工作走失败处理。完整分支以函数为准，恢复候选仍取决于后台能力。

Python 里的 `asyncio.Task` 对象不会因为你把任务描述写到 JSON 就自动跨进程恢复。项目同样必须显式保存关联并选择恢复策略，不能无差别重新执行外部操作。

## 5. 本讲检查题

1. 共享配置和记忆，是否等于共享工作状态？
2. 事件回放为什么不等于重新执行命令？
3. 开始新对话、客户端重连与 Gateway 重启分别改变什么？
4. 一个提醒与一个正在写外部文件的任务，为什么不能采用相同的重跑策略？

从目录表、协议回放、会话说明和恢复源码分别给出依据。若要进一步研究默认值，沿“配置解析 → 装配实参 → 类内部行为”读；只看构造器默认值不足以确认实际部署设置。
