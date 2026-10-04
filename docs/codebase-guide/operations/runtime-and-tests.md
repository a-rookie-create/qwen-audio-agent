# 第 8 讲：运行、诊断与验证理解

[讲义入口](../README.md) · 上一讲：[客户端与扩展](../subsystems/clients-and-extensions.md) · 后续：[练习](../exercises/reading-workbook.md)、[历史](../02-history-reading-route.md)

本讲回答：**如何用一次实际操作验证前面所读，发生问题时从哪层查起？**

## 1. 操作步骤直接读原文

| 顺序 | 原文 | 用途 |
| --- | --- | --- |
| 1 | [安装与升级](../../getting-started/install.zh.md) | 选择运行环境与安装方式；源码运行要求在“从源码安装” |
| 2 | [快速开始](../../getting-started/quickstart.zh.md) | 按原步骤完成普通对话，再按需要添加后台 |
| 3 | [配置总览](../../configuration.zh.md) | 核对配置优先级、准确路径和实际实例 |
| 4 | [Gateway 运行](../../operations/gateway.zh.md) | 选择运行方式、应用配置、检查状态和理解进程所有权 |
| 5 | [故障排查](../../operations/troubleshooting.zh.md) | 沿连接、音频、后台与远程边界收集证据 |

具体命令、参数、支持版本与配置例子在原文中执行和查阅，本讲不重新维护第二份安装教程。开发脚本的实际命令看[根 package.json](../../../package.json)，工程检查读[贡献指南](../../../CONTRIBUTING.md)。

## 2. 讲义补充：验证一条链路时，每次增加一个环节

你可以先理解并验证普通前台对话，再增加一项前台工具，再增加后台工作，最后研究记忆或远程客户端。这个顺序是教学安排，便于把新增依赖和失败位置关联起来。

Python 中“Web 服务已监听”“数据库连接成功”“某次事务提交成功”也是三个不同检查点。在这里同样要把 Gateway 可达、GCP 握手、实时模型连接、工具操作、后台工作和结果呈现逐层判断。相关证据分别由[Gateway 检查](../../operations/gateway.zh.md#检查运行情况)、[协议握手](../../gateway-protocol.zh.md#3-连接与能力协商)、[工作指南](../../guides/tasks.zh.md#看懂工作状态)和[结果交付](../../architecture/deep-dive.zh.md#7-最终结果交付)解释。

比如“受理了但一直没有结果”，先问工作记录是否完成；如果完成，再沿通知与播放找证据。不要只重复检查模型 Key。日志入口、关联信息与反馈方式已在[故障排查](../../operations/troubleshooting.zh.md)中给出。

## 3. 自动化测试能帮你理解什么

先读[前台 Runtime 评测](../../reference/frontend-evaluations.zh.md)：它解释确定性运行时验证与模型语义质量的区别。再读[Provider 的行为验证](../../voice-frontends/custom-provider.zh.md#行为验证)和[Backend SDK 的 Conformance](../../reference/backend-adapter-sdk.zh.md#conformance)，理解“共同契约”怎样保护可替换接口。

Python 类比是用 fake client 测自己的业务服务：可以证明状态转换、取消和事件处理，却不能据此证明真实远端模型一定选择正确工具。读测试时找真实生产对象、模拟边界和断言，避免把 fixture 的输出当成产品能力。

按问题选择现有测试作为代码阅读入口：

| 想验证的理解 | 现有测试源码 |
| --- | --- |
| 前台会话与工具事件 | [会话运行时测试](../../../server/test/realtime-session-runtime.test.mjs)、[工具调用测试](../../../server/test/tool-call-handler.test.mjs) |
| Task 受理、调度与取消 | [任务管理测试](../../../server/test/task-manager.test.mjs)、[任务操作测试](../../../server/test/task-operations.test.mjs) |
| 结果生成与播放确认 | [播报测试](../../../server/test/announcement-manager.test.mjs)、[呈现测试](../../../server/test/realtime-presentation-runtime.test.mjs) |
| 存储、重连和恢复 | [任务存储](../../../server/test/task-store.test.mjs)、[会话日志](../../../server/test/session-journal.test.mjs)、[会话任务协调](../../../server/test/session-task-coordinator.test.mjs) |
| 外部能力与模块边界 | [Provider 行为](../../../server/test/realtime-provider-behavior.test.mjs)、[依赖方向](../../../server/test/dependency-boundaries.test.mjs)、[模块裁剪](../../../server/test/optional-modules-pruning.test.mjs) |

这是选读表，不表示本轮运行了这些测试。首次分析的已执行记录单列在[验证记录](analysis-validation.md)，真实模型、硬件和示例业务仍需各自验证。发布/CI 的完整检查范围看[原 CI 配置](../../../.github/workflows/ci.yml)。

## 4. 本讲检查题

1. 改了配置未生效，应先核对哪些文件、环境和实例？
2. Gateway 可达，为什么仍可能无法对话或执行后台工作？
3. Mock 测试通过与真实模型选对工具，有什么证据范围差别？

先从对应原文找答案，再为自己选择一个可验证的检查点。八讲读完后，用[练习页](../exercises/reading-workbook.md)把架构、流程、状态和扩展连成一页笔记。
