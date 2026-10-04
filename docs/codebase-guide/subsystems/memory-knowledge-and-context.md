# 第 5 讲：记忆、知识与上下文

[讲义入口](../README.md) · 上一讲：[后台工作](../flows/tasks-permissions-and-delivery.md) · 下一讲：[状态与恢复](../data/state-and-persistence.md)

本讲回答：**助理知道的内容从哪里来？哪些内容能影响行为，哪些只是回答依据？**

## 1. 按“体验 → 边界 → 实现”读原文

| 顺序 | 原文 | 本次关注 |
| --- | --- | --- |
| 1 | [助手画像与偏好](../../reference/personalization.zh.md) | 临时要求、长期偏好、默认人设与事实分别放在哪里 |
| 2 | [长期记忆](../../reference/memory.zh.md) | 明确写入、会后自动整理、会话回溯的区别 |
| 3 | [Memory Provider](../../reference/memory-provider.zh.md) | 开头的四层上下文与优先级；“替换记忆 Provider” |
| 4 | [资料库指南](../../guides/knowledge.zh.md)及[知识库 Provider](../../reference/knowledge.zh.md) | 用户文档如何进入检索，检索与管理为何分开 |

原文已给出文件、接口、配置与能力表，按上述顺序读完整条件。进一步研究观察推断时再看[偏好学习机制](../../reference/preference-learning.zh.md)。

## 2. 讲义补充：先按用途归类，不按存储方式归类

Python 中两个 `str` 都能放进提示词，却可能一个是规则、一个是引用资料；同为字符串不表示同样可信。同样，几个文件都使用 Markdown，也不表示它们具有同样权限。

带着下面几句话回到原文做分类练习：

| 教学输入 | 到原文查哪个边界 |
| --- | --- |
| “这次简短一点”与“以后回答简短一点” | [个性化](../../reference/personalization.zh.md)：当前要求与持久偏好 |
| “我住在杭州” | [Memory Provider](../../reference/memory-provider.zh.md)：事实材料与行为指令 |
| “购物清单加牛奶” | [清单指南](../../guides/notes-reminders.zh.md)：条目集合与长期记忆 |
| 上传一本产品手册 | [资料库指南](../../guides/knowledge.zh.md)：资料导入与检索 |
| “刚才那项工作完成了吗” | [后台工作指南](../../guides/tasks.zh.md)：当前任务台账与旧聊天回顾 |

这里的分类练习帮助把原本分散的文档接起来。**回答依据、用户偏好、命名集合、任务事实分别由对应模块维护。** 原文中的信任优先级仍要逐项阅读。

## 3. 三条写入路径与一个消费边界

将[长期记忆“自动整理”](../../reference/memory.zh.md#自动整理)、[个性化“可选偏好学习”](../../reference/personalization.zh.md#可选偏好学习)和[偏好学习机制](../../reference/preference-learning.zh.md)并排阅读：用户明确要求、会后整理明确内容、跨会话观察推断，使用的证据和开关不同。它们不能用一个“自动记忆”概念替代。

Python 理解锚点是 service / repository 分工：多个入口都通过服务更新存储，前台通过统一接口消费上下文；不能每个入口自己写文件。原文 Memory Provider 的工具、API 控制面、学习观察和变更通知正好说明这条边界。源码验证入口是 [FrontendMemoryRuntime](../../../server/src/memory/runtime.mjs)与 [Provider 契约](../../../server/src/memory/provider.mjs)。

原文还要求 `list()` 同步返回有界快照，`observeAudio()` 在音频热路径只做有界内存操作。可以类比 Python 的录音回调：在回调里等待远程数据库会拖住输入；远程学习和刷新应留到适当的异步边界。具体哪些方法允许异步及谁接管学习，直接看[Provider 原文](../../reference/memory-provider.zh.md#替换记忆-provider)。

## 4. 知识接口与检索算法分开理解

如果你用过 Python 的 RAG，可能会想到 Embedding 或向量库。这里应先读[知识 Provider 的“内置基础实现”](../../reference/knowledge.zh.md#内置基础实现)：默认本机实现是文本转换、分块与关键词检索。统一 Provider 接口不规定某种算法。

再读同文的“检索”和“入库和管理”：模型查询与用户管理有不同入口；模型请求中的查询参数与运行时提供的 owner / 取消信号有不同来源。Python 类比是 `retrieve(query, context)` 的两个参数：业务输入不能自行覆盖可信身份。

外部算法和服务接入读[LightRAG 原文](../../scenarios/lightrag.zh.md)及[示例 README](../../../examples/lightrag/README_ZH.md)；记忆替换读[VoiceMem](../../scenarios/voicemem.zh.md)与[Memcode](../../scenarios/memcode.zh.md)。Python 服务可以在外部实现能力，Node Adapter 负责转成框架接口；详细接法见[第 7 讲](clients-and-extensions.md)。

## 5. 本讲检查题

1. 临时要求、长期偏好与事实记忆为什么不能混放？
2. 明确保存、会后整理与偏好推断分别需要什么证据？
3. 为什么远程 Memory Provider 仍需要本地同步快照？
4. 默认资料库是不是向量数据库？更换外部检索算法要改哪条边界？

答案依据分别在个性化、记忆/偏好学习、Memory Provider、Knowledge Provider 原文中。接口源码按需查[代码索引](../key-code-index.md)。
