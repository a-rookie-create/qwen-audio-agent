# 读懂智能座舱：项目方案与技术实现

这套笔记围绕一个目标展开：能够讲清 **smart-cockpit 做了什么、为什么这样设计、每个模块靠什么技术实现**，并把这些理解转化为项目介绍与面试回答。正文从用户场景讲起，源码与测试放在末尾的“事实对照”中，按需查看即可。

smart-cockpit 是原 JavaScript / React 项目，qwen-audio-agent 是它复用的语音与任务运行框架。这套笔记以两者的原实现为依据。

## 从这里开始读

先读 [00：项目全貌与框架基础](00_project_and_framework.md)，建立四个进程与三个逻辑角色的认识，再顺着下面的路线读。每篇底部都有上一页和下一页。

| 顺序 | 这一篇回答什么 |
|---|---|
| [00 项目全貌与框架基础](00_project_and_framework.md) | 项目提供哪些能力？qwen-audio-agent 在其中做什么？ |
| [01 前台语音交互与任务分流](01_voice_and_task_routing.md) | 一句话怎样变成操作？长任务为什么不阻塞聊天？ |
| [02 业务 Service 与统一状态](02_business_service_and_state.md) | 语音与按钮怎样操作同一辆“车”？状态由谁保存？ |
| [03 车控、音乐与天气](03_vehicle_music_and_weather.md) | 日常座舱能力怎样设计成模型可以使用的工具？ |
| [04 导航与位置服务](04_navigation_and_location.md) | 地点怎样变成路线？多途经点与偏好修改怎样实现？ |
| [05 后台 Agent 与资料研究](05_background_agent_and_research.md) | 模型怎样连续使用工具？进度、取消、报告怎样返回？ |
| [06 闪购与订单确认](06_flashbuy_and_confirmation.md) | 如何区分浏览、加购和下单？确认如何落到业务层？ |
| [07 自定义技能与环境事件](07_custom_skills_and_environment_events.md) | 一句自定义口令怎样执行多个步骤？温度提醒怎样触发？ |
| [08 记忆、人设与上下文](08_memory_persona_and_context.md) | 助手怎样记住用户？哪些信息持久化，哪些只是当前状态？ |
| [09 客户端与界面联动](09_client_and_voice_ui_sync.md) | 地图、3D 车辆、语音播放和任务面板怎样与执行结果同步？ |
| [10 工程装配与评测](10_engineering_and_evaluation.md) | 项目怎样启动、扩展和验证？准确率与时延怎样理解？ |
| [11 项目介绍与简历表达](11_project_story_and_resume.md) | 怎样把整套方案连成一段介绍，展开技术亮点与取舍？ |

只有五分钟时，读 **00 + 11**，先获得整体认识。约半小时的重点路线是 **00 → 01 → 02 → 05 → 07 → 08**，它能串起系统的主要设计。完整阅读按编号顺序进行；导航、闪购、界面和评测可以根据面试方向反复查看。

## 先记住这一句话

**实时模型负责交流和选择工具，框架负责会话与异步任务，座舱 Service 负责业务执行和状态，客户端负责声音与界面。** 后台 Agent 是单独的办事服务，使用自己的模型完成多步工作。

图均直接嵌入 PNG 图片，点击“放大查看”即可查看原图。可编辑的 SVG 源图保存在同一目录的 `assets/` 中。

## 图里常见的词

| 词 | 在这个项目里怎样理解 |
|---|---|
| Realtime | 实时语音模型服务，接收输入并持续输出回复，也能提出工具调用。 |
| Function Calling | 模型提出“用哪个工具、传什么参数”，程序执行后把结果交回模型。 |
| Gateway | 框架服务入口，承载前台会话、任务编排和模型/后台接入。 |
| WS / WebSocket | 持续的双向连接，这里用于客户端与 Gateway 的音频和对话事件。 |
| GCP | Gateway Client Protocol，框架约定的客户端消息格式，不是 Google Cloud。 |
| HTTP / SSE | HTTP 获取快照或提交操作；SSE 是服务器向界面持续推送状态的单向通道。 |
| MCP | 统一发现、描述和调用工具的协议，这里连接座舱业务能力。 |
| A2A / ACP | 后台 Agent 的接入协议；座舱默认使用 A2A，框架也支持 ACP 等适配方式。 |
| Provider / Adapter | 适配接口，把不同模型或服务转换成框架能使用的能力。 |
| Artifact | 后台任务交付的完整结果，例如文字报告；可以与简短口播摘要分开。 |
| Harness | 使用生产提示词与框架执行链路进行评测的运行环境。 |

<details>
<summary>核对范围与依据</summary>

本套文档核对日期：**2026-10-07**。分析的仓库提交：`343c478b137b6db59e4142a0591e11fc879cc8f6`。

核对范围为 `examples/smart-cockpit/`，以及它使用的 qwen-audio-agent 公开接口与相关运行时。GitNexus 状态为本仓库未建立索引，因此依据本地配置、源码、现有测试和维护中的结果记录核对。

“事实对照”中的源码链接表示静态核对，测试链接表示仓库已有相应验证场景。本次整理没有重跑真实模型、地图 API 或实车测试；第 10 篇的数字明确引用仓库历史记录。模型的实际工具选择、服务可用性和语音体验，需要运行项目时验证。

主要实现入口：

| 职责 | 实现位置 |
|---|---|
| 框架服务装配 | [createGatewayApplication](../../../../server/src/app/gateway-application.mjs#L63) |
| 座舱 Gateway 装配 | [gateway/server.mjs](../../gateway/server.mjs) |
| 语音采集与播放 | [useVoiceSession](../../client/src/hooks/useVoiceSession.js) |
| 场景业务与共享状态 | [CockpitService](../../service/cockpit-service.mjs)、[CockpitStateStore](../../service/state-store.mjs) |
| 工具目录与领域分流 | [registry.mjs](../../service/tools/registry.mjs)、[surface-routing.json](../../service/tools/surface-routing.json) |
| 后台模型执行 | [CockpitAgentExecutor](../../agent/executor.mjs)、[DashScopeCockpitModel](../../agent/model.mjs) |
| 场景技能与温度规则 | [CustomSkillStore](../../service/custom-skills/store.mjs)、[TemperatureSkillRules](../../service/custom-skills/temperature-rules.mjs) |
| 框架记忆运行时 | [FrontendMemoryRuntime](../../../../server/src/memory/runtime.mjs#L53) |
| 场景运行预检与评测 | [bootstrap/preflight.mjs](../../bootstrap/preflight.mjs)、[bench/README.md](../../bench/README.md) |

</details>
