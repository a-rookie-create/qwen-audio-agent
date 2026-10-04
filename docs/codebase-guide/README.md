# qwen-audio-agent 项目理解讲义：给 Python 使用者

这份讲义把散落的项目文档串成一条学习路线。**项目已有的定义、架构、配置、协议和使用说明，直接打开原文阅读；这里补充阅读目的、文档之间的联系、Python 类比和检查题。** 原文中的完整条件和例外保留在链接目标中。

## 现在从哪里开始

先打开项目自带的[架构总览](../architecture/overview.zh.md)，只读“核心逻辑架构”和“Gateway 与客户端”。然后看[第 1 讲的解读](00-system-overview.md)：借助 Python 的服务对象、接口和进程概念，理解原文中的职责划分。

**这一步的目标只有一个：说清系统由谁负责交流、谁负责衔接、谁负责办事，以及客户端和 Gateway 放在哪里。** 检查题答清后，再进入下一讲。

## 八讲主线

| 顺序 | 讲义 | 要解决的问题 | 本讲主要原文 |
| --- | --- | --- | --- |
| 1 | [整体架构](00-system-overview.md) | 项目目标是什么，各角色怎样分工？ | [项目 README](../../README_ZH.md)、[架构总览](../architecture/overview.zh.md) |
| 2 | [架构怎样落到代码与启动入口](03-architecture-and-entrypoints.md) | 从哪里启动，谁创建和连接各模块？ | [源码导航](../../server/src/README.md)、[依赖方向](../architecture/deep-dive.zh.md#9-依赖方向) |
| 3 | [实时对话与前台工具](flows/voice-and-tools.md) | 一句话如何得到回复，何时调用工具？ | [对话与附件](../guides/conversation.zh.md)、[实时边界](../architecture/deep-dive.zh.md#3-实时边界) |
| 4 | [后台工作与结果回流](flows/tasks-permissions-and-delivery.md) | 对话怎样与办事并行，权限和结果如何衔接？ | [后台工作与授权](../guides/tasks.zh.md)、[详细架构](../architecture/deep-dive.zh.md) |
| 5 | [记忆、知识与上下文](subsystems/memory-knowledge-and-context.md) | 助手怎样记住用户，资料从哪里来？ | [个性化](../reference/personalization.zh.md)、[记忆](../reference/memory.zh.md)、[资料库](../guides/knowledge.zh.md) |
| 6 | [状态、持久化与恢复](data/state-and-persistence.md) | 谁保存什么，换客户端或重启后发生什么？ | [配置与数据目录](../configuration.zh.md#配置与数据目录)、[回放](../gateway-protocol.zh.md#8-回放错误与限制) |
| 7 | [客户端、扩展与场景](subsystems/clients-and-extensions.md) | 如何换模型、后台、界面，Python 能接在哪？ | [扩展总览](../extensions.zh.md)、[客户端协议](../gateway-protocol.zh.md)、[示例索引](../scenarios/index.zh.md) |
| 8 | [运行、诊断与验证](operations/runtime-and-tests.md) | 怎样验证自己理解的链路，问题属于哪层？ | [安装](../getting-started/install.zh.md)、[快速开始](../getting-started/quickstart.zh.md)、[故障排查](../operations/troubleshooting.zh.md) |

每讲按“带着问题打开原文 → 阅读讲义补充 → 回答检查题 → 按需看源码”进行。源码定位是验证入口，第一遍只看本讲指定的少量符号。

## 按自己的时间选择

| 时间 | 阅读范围 | 预期收获 |
| --- | --- | --- |
| 5 分钟 | 架构总览前两节 + 第 1 讲 | 建立整体职责地图 |
| 30 分钟 | 第 1～3 讲的必读原文和补充；遇到语法查 JS 桥梁 | 把职责地图接到启动、普通对话和工具调用 |
| 分次完整学习 | 按八讲顺序，每次完成一讲的检查题 | 覆盖架构、核心流程、数据、部署与扩展；再用历史解释演进 |

时间是阅读安排，不是保证。遇到不熟悉的 JS 表达式，查[Python 到 JavaScript 阅读桥梁](01-python-to-javascript.md)的对应节即可；它是本讲义针对你的语言背景补充的教材。

## 随时可查的附录

- [原文阅读地图](source-reading-map.md)：按主题汇总原项目文档，标明用途与进阶入口。
- [Python 到 JavaScript](01-python-to-javascript.md)：导入、对象、异步、回调、事件、类与少量 React。
- [12 阶段 Git 历史路线](02-history-reading-route.md)：已有整体地图后，回看重要版本和功能转折。
- [学习练习](exercises/reading-workbook.md)：各讲检查题的参考依据，以及可选 Python 教学模型。
- [代码定位索引](key-code-index.md)：文件、符号、基线行号与职责。
- [证据与版本](evidence-and-history.md)：源码基线、分析范围、测试记录与标签表。

## 怎么区分原文与补充

**原文**是项目维护者提供的文档与配置；链接旁写清应读的章节。**讲义补充 / teaching** 是面向 Python 使用者的解释、类比与练习，帮助理解原文，不是新的项目契约。**源码定位 / static** 用于核对文档中的机制。已执行的测试单独标明日期与范围，未执行的只作为阅读入口。

讲义修订日期：2026-10-04，Asia/Shanghai。源码分析基线：`f6dd0e3703d58e4941159c1be89447f3fcb5063a`（包版本 `2.0.1`）；首次源码分析日期为 2026-10-03。其后的提交只修改本讲义，源码行号仍按该基线核对。原文使用仓库内相对链接；固定源码行号使用该提交的链接。

原文、历史规划、示例和代码有不同语境。遇到不一致，记录具体章节，回到该基线的配置、装配和实现核对。真实模型、音频设备和远端 Agent 的表现仍需实际接入；本讲义的验证范围见[证据记录](evidence-and-history.md)。
