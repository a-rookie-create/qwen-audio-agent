# 第 4 讲：后台工作、权限与结果回流

[讲义入口](../README.md) · 上一讲：[对话与工具](voice-and-tools.md) · 下一讲：[记忆与知识](../subsystems/memory-knowledge-and-context.md)

本讲从前台实际提交后台工作开始，回答：**办事为什么不挡住对话，结果怎样回到同一个助理？**

## 1. 先读用户流程，再读实现约束

| 顺序 | 原文 | 本次阅读重点 |
| --- | --- | --- |
| 1 | [后台工作与授权](../../guides/tasks.zh.md) | 发起、继续、查询、取消；等待输入与权限的用户体验 |
| 2 | [详细架构](../../architecture/deep-dive.zh.md) | 第 2 节“非阻塞请求流”、第 5 节“Task 状态”、第 7 节“最终结果交付” |
| 3 | [Backend Adapter SDK](../../reference/backend-adapter-sdk.zh.md#backendport) | 工作指令、标准结果、事件、权限与补充输入的边界 |

具体状态机、权限范围和 Adapter 方法面直接读原文。下面连接这些原文中容易被当成一件事的几个阶段。

## 2. 讲义补充：Python 的 await 放在哪里很关键

你可以用 `asyncio.Queue.put_nowait()` 理解“受理请求”，用 worker 的执行协程理解“处理工作”。前台等待的是受理回执，而不是 worker 的最终结果。即使函数写着 `async`，如果一路 `await` 到长任务结束，对话入口仍会等它；关键要看等待边界。

在源码中分别找：

| 代码定位 | 验证哪个阶段 |
| --- | --- |
| [AgentTaskRuntime.executeSpawnThinkingToolCall](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L195) | 解析目标与附件引用，生成受理回执 |
| [TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57) | 把任务管理与后台执行连接起来 |
| [TaskManager.create / #create](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L428) | 保存 queued 快照，安排后续调度，返回快照 |
| [TaskManager.start](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L623) | 后续真正执行、处理事件与终态 |

这组定位解释原文“受理即回”，不是承诺网络或模型零延迟。JS `Promise`、Python coroutine 与 microtask 的区别见[语言桥梁第 5 节](../01-python-to-javascript.md#5-最关键差异promise-与-asyncawait)。

再对照原文“固定后端 Agent Session”和“后端内部能力”：ACP 的协调 Session 可以串行接收请求，再向独立 Session 委派；被验证的委派允许入口通道释放，目标工作仍继续。它属于 ACP Adapter 的内部实现，不能把这套拓扑套到每个后台。A2A 的映射读[A2A Adapter 原文](../../reference/a2a-backend-adapter.zh.md)。

## 3. 权限与补充输入：从实际请求建立关联

把[用户授权说明](../../guides/tasks.zh.md#允许与拒绝)、[BackendPort 事件契约](../../reference/backend-adapter-sdk.zh.md#backendport)和[核心 Prompt](../../../config/frontend-agent/PROMPT.md)的 `Background work` / `Permission requests` 放在一起读。

Python 类比是请求表：程序收到真实请求，存下它属于哪项工作；用户回复后按关联查找，再把决定传给执行服务。模型的一句“已经同意”不是这张请求表里的事实。源码入口是 [PermissionPolicy](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/permission-policy.mjs#L9)和 [TaskOperations](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L34)。

读“后台问了一个问题”时还要区分两种情况：SDK 中的结构化 `backend.input.requested` 保持当前 Task 活动，由 `respondInput` 恢复；一个已经结束的后台回合也可能用自然语言提出后续问题，再以续办关系提交。Prompt 分别规定对应路径。**先识别运行时收到的事件和状态，再解释聊天文本。**

前台工具的确认与鉴权归相应服务，后台权限策略归后台工作链。完整适用范围分别在[前台 MCP](../../reference/frontend-mcp.zh.md#支持范围与安全)、[OpenAPI](../../reference/frontend-openapi.zh.md#支持边界)与后台授权原文中。

## 4. 讲义补充：完成与交付是两条状态轴

在 Python 中，worker 把结果放入队列，不代表消费者已经取走，更不代表扬声器播放了它。这对应项目中的工作状态与通知状态：一项工作可以已经完成，但结果尚在等待合适的对话窗口。

先读[原文“最终结果交付”](../../architecture/deep-dive.zh.md#7-最终结果交付)，再看 [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12)怎样领取通知，以及[播报管理器](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-manager.mjs#L351)怎样安排投递。

原文重点说明普通音频结果由 `playback.started` 确认开始交付。源码还有纯文字/非语音结果完成以及显式 `user_interruption` 的消费分支，见 [RealtimePresentationRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-presentation-runtime.mjs#L62)。因此通知的 `delivered` 要结合呈现路径理解；不能统一解释为“用户听完”。这是对原文重点路径的源码补充（static）。

## 5. 断连、取消与失败放在各自边界理解

[对话指南](../../guides/conversation.zh.md#历史与新会话)讲用户如何开始新对话；[源码导航](../../../server/src/README.md)讲前台关闭时清理哪些资源；[后台工作指南](../../guides/tasks.zh.md)讲显式取消。三者组合说明：对话连接和已受理工作有不同生命周期。

失败也按阶段判断：没有成功受理、后台执行失败、结果已经完成但投递失败，是不同问题。分别回到受理回执、Task 状态和通知/播放事件找依据；不要用一句界面文案替代三类状态。

## 6. 本讲检查题

1. `accepted` 证明了什么，尚未证明什么？
2. `delegated` 为什么既可以释放入口通道，又仍是活动工作？
3. 当前 Task 在等用户输入，为什么不应再发起一份重复工作？
4. 工作 completed 后，结果为什么还能等待播报？
5. 新建前台对话、断开客户端与取消后台工作有什么区别？

可选练习：运行[Python 教学模型](../exercises/reading-workbook.md#3-可选-python-练习只演示一项后台工作)。它只帮助理解受理、执行与交付，不模拟完整语音系统。
