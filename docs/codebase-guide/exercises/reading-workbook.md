# 学习练习：每次只完成一讲

[讲义入口](../README.md)

## 1. 学习顺序与笔记模板

按[八讲主线](../README.md#八讲主线)读。每讲先打开指定原文，读完补充解释后，合上讲义，用自己的话回答检查题。不能回答时，返回该题对应原文，不急着继续增加代码细节。

每讲留下一份短笔记：

```text
本讲的问题：
原文文件与章节：
我用 Python 概念怎样理解它：
这个类比在哪一点不再适用：
涉及的角色 / 状态 / 接口：
一个代表性源码定位（可选）：
我还不能解释的问题：
```

第一遍建立完整地图；第二遍选一条具体调用链；已有当前地图之后再看[Git 历史](../02-history-reading-route.md)。不需要同时复现所有旧版本。

## 2. 各讲检查题的参考依据

下面是答题要点，用于检查你是否抓住关系；完整定义、条件和例外仍在原文。

### 第 1 讲：整体架构

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 前台组织对话与工具，WebUI 处理 I/O 和展示。见[架构总览](../../architecture/overview.zh.md)。 |
| 2 | 编排通过代码管理状态和调度；逻辑组件不意味着新增模型。见同文“核心逻辑架构”。 |
| 3 | Gateway 是装配与接入宿主，属于运行形态。见同文“Gateway 与客户端”。 |
| 4 | 仅前台模式仍支持聊天和实际启用且模型支持的前台工具。见[基本概念](../../getting-started/concepts.zh.md#不配置后台也能用)。 |
| 5 | 收音在手机环境；前台处理在 Gateway 接入的模型链路；后台在配置的执行环境。具体部署见[基本概念](../../getting-started/concepts.zh.md#本机与远程)。 |

### 第 2 讲：启动与装配

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 组合根选择实现，业务模块依赖契约，避免绑定供应商。见[依赖方向](../../architecture/deep-dive.zh.md#9-依赖方向)。 |
| 2 | 两种入口复用任务操作、权限和执行链，回执仍由各入口产生。见[源码导航](../../../server/src/README.md)。 |
| 3 | 每连接有自己的前台运行时，共用 Task 服务仍管理任务事实。见同文“前台会话与传输”。 |
| 4 | 会执行模块顶层语句；bootstrap 在顶层创建应用。见[bootstrap 源码](../../../server/src/app/bootstrap.mjs)和[语言桥梁](../01-python-to-javascript.md#2-导入导出与模块执行)。 |

### 第 3 讲：对话与工具

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 普通对话不必须创建后台工作。见[对话指南](../../guides/conversation.zh.md)。 |
| 2 | 定义描述调用形式，可用性限制当前工具面，handler 执行并校验。见[实时边界](../../architecture/deep-dive.zh.md#3-实时边界)与[工具源码](../../../server/src/frontend/tools/tool-call-handler.mjs)。 |
| 3 | 搜索是前台工具能力。见[联网搜索](../../guides/web-search.zh.md)。 |
| 4 | 附件和实时帧的通道、消费者及生命周期不同。见[视觉输入](../../guides/vision.zh.md)。 |
| 5 | 生成事件描述模型状态，播放还取决于设备与客户端回执。见[架构演示](../../voice-agent-architecture-presentation.zh.md)中的 `response.done` 与播放说明。 |

### 第 4 讲：后台工作

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 已受理请求，尚不证明执行完成。见[后台工作指南](../../guides/tasks.zh.md#看懂工作状态)。 |
| 2 | 委派把独立执行关联到原工作，通道可释放，原 Task 生命周期仍继续。见[最终结果交付](../../architecture/deep-dive.zh.md#7-最终结果交付)。 |
| 3 | 结构化请求属于当前 Task，应把回复送回同一工作。见[BackendPort](../../reference/backend-adapter-sdk.zh.md#backendport)和[核心 Prompt](../../../config/frontend-agent/PROMPT.md)。 |
| 4 | 执行完成与结果消费不同；对话窗口、模型表达与播放仍需安排。见[最终结果交付](../../architecture/deep-dive.zh.md#7-最终结果交付)。 |
| 5 | 对话生命周期与后台工作分开；显式工作控制才取消 Task。见[对话指南](../../guides/conversation.zh.md#历史与新会话)和[源码导航](../../../server/src/README.md)。 |

### 第 5 讲：记忆与知识

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 当前要求、持久偏好与事实的有效期和行为权威不同。见[个性化](../../reference/personalization.zh.md)、[Memory Provider](../../reference/memory-provider.zh.md)。 |
| 2 | 明确保存依据用户要求；会后整理依据明确内容；推断还需证据和跨会话条件。见[长期记忆](../../reference/memory.zh.md)、[偏好学习](../../reference/preference-learning.zh.md)。 |
| 3 | 实时上下文读取不等待远程 I/O；远端 Adapter 维护有界快照。见[Memory Provider](../../reference/memory-provider.zh.md#替换记忆-provider)。 |
| 4 | 内置基础实现是文本分块和关键词检索；外部算法接 Knowledge Provider。见[知识库 Provider](../../reference/knowledge.zh.md#内置基础实现)。 |

### 第 6 讲：状态与恢复

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 用户数据可共享，实例运行状态仍隔离。见[配置目录](../../configuration.zh.md#配置与数据目录)。 |
| 2 | 回放重建已记录事实，再执行命令会重复外部副作用。见[协议回放](../../gateway-protocol.zh.md#8-回放错误与限制)和[恢复源码](../../../server/src/task/task-recovery.mjs)。 |
| 3 | 新对话改变对话语境；重连重建连接级资源；重启重建应用级资源。分别读[基本概念](../../getting-started/concepts.zh.md)、[源码导航](../../../server/src/README.md)和[Task 状态](../../architecture/deep-dive.zh.md#5-task-状态)。 |
| 4 | 提醒可以重新安排；外部写入不能无差别重做，需恢复关联或明确失败。见[taskRecoveryAction](../../../server/src/task/task-recovery.mjs)。 |

### 第 7 讲：客户端与扩展

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 检索接 Knowledge Provider；业务 API 可用 MCP/OpenAPI；持续执行接 BackendPort。桥接需满足各自契约。见[扩展总览](../../extensions.zh.md)。 |
| 2 | 三者分别接实时模型、办事服务、客户端；消息和生命周期不同。见[架构接口边界](../../architecture/overview.zh.md#接口边界)。 |
| 3 | 网络连接、应用握手与模型连接分别有就绪条件。见[客户端协议](../../gateway-protocol.zh.md#3-连接与能力协商)和[Gateway 检查](../../operations/gateway.zh.md#检查运行情况)。 |
| 4 | 找通用接入点，再找示例新增工具/状态/策略，最后读验证限制。见[示例索引](../../scenarios/index.zh.md)及所选示例原 README。 |

### 第 8 讲：运行与验证

| 题号 | 要点与原文 |
| --- | --- |
| 1 | 实际文件、配置优先级、进程环境、正在连接的 Gateway 及重启方式。见[配置总览](../../configuration.zh.md)、[运行与常驻](../../operations/gateway.zh.md)。 |
| 2 | 服务可达只证明入口可访问；模型、后台、设备与工具各有依赖。见[故障排查](../../operations/troubleshooting.zh.md)。 |
| 3 | Mock 保护内部确定性行为，模型语义质量需要独立评测。见[前台 Runtime 评测](../../reference/frontend-evaluations.zh.md)。 |

## 3. 可选 Python 练习：只演示一项后台工作

在仓库根目录运行：

```bash
python3 docs/codebase-guide/exercises/nonblocking_demo.py
```

只需要 Python 3.10+ 标准库。脚本不接真实模型、网络或 Gateway，也不读写配置。它用固定结果模拟“整理会议纪要”，把受理、执行、等待空闲、生成与播放确认放在不同协程里。

先预测三件事：受理是否先于最终完成；后台执行时对话是否仍继续；工作完成后通知是否还可能等待。运行后给 `status` 与 `notification` 各画一条时间轴。

这是 **teaching**：脚本没有真实语音、模型选择工具、自然打断、文档处理、权限、owner 隔离、委派、持久化与重连。它只帮助理解第 4 讲的一个分支，不能替代原项目实现或测试。

## 4. 完整项目理解的最后一页

用一页纸写下：产品目标；三个逻辑角色与 Gateway/客户端；启动装配；普通对话、前台工具、后台工作；记忆与知识；状态与恢复；模型/后台/客户端的扩展接口；配置和验证。

每项旁边放一个**原文链接**，需要时再补一个代码符号。这样得到的笔记仍能返回完整原文，不会把讲义的简化类比当成完整契约。
