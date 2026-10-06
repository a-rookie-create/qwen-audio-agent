# 三条主路径，先读懂思想

先读 [overview.py](../overview.py)。箭头表示职责交接，不要求每个箭头
都是一个真实 Python 函数，也不表示所有处理同步发生。
原符号与行号见 [源码对照表](source_map.md)。

## 启动：把对象接起来

座舱准备配置与后台接入对象，调用框架的 Gateway 装配入口。
Gateway 准备共用任务管理、后台执行、前台工具来源等服务。
客户端连接进来，再创建自己的实时会话。

读 [座舱组装](../gateway/server.py) → [框架接线](../framework_reference/gateway_application.py)。

## 1. 普通聊天

```text
客户端收音 → Gateway 当前会话 → 实时模型
→ 会话收到模型回复 → 客户端展示、播放
```

普通聊天无需创建后台任务。前台模型结合人设、上下文、工具构成前台 Agent，
客户端提供 I/O。播放完成由客户端报告，收到音频不等于用户已经听完。

读 [语音客户端](../client/voice_session.py) → [实时会话](../framework_reference/frontend_session.py)。

## 2. 前台工具调用

```text
实时模型选择工具 → 工具处理器 → 前台 MCP
→ Service 业务函数 → 更新业务状态
→ 工具结果回到实时模型 → 自然回复
```

例如温度控制。工具真实执行后，模型才能依据结果回答。
状态变化同时经 Service SSE 更新 UI，这条状态链不经过 Gateway。
未知工具、参数错误、操作失败不能被表述为成功。

读 [工具分叉](../framework_reference/frontend_session.py) →
[MCP 入口](../service/mcp_server.py) → [业务执行](../service/cockpit_service.py) →
[业务状态](../service/state_store.py)。

## 3. 委派后台工作

```text
实时模型调用 spawn_thinking → 创建任务、排队 → 立即返回提交回执
                                        ↓
                              后台 Agent 执行模型/工具循环
                                        ↓
                           记录完成或失败 → 安排结果回到对话
```

任务管理决定何时执行，后台适配器负责联系 Agent，Agent 决定如何使用工具。
前台得到回执即可继续对话。执行完成、送入模型、用户听到结果分别处理。
失败或取消不自动回滚已经执行的业务操作；应查询真实业务状态。

读 [任务管理](../framework_reference/task_runtime.py) →
[后台接入](../framework_reference/backend_adapter.py) → [模型循环](../agent/executor.py)。

## 其他行为按需展开

| 行为 | 思想 | 学习入口 |
|---|---|---|
| 面板点击 | 直接 HTTP 调用 Service，再通过 SSE 更新 UI | [客户端业务状态](../client/cockpit_state.py) |
| 人设切换 | 注册事件更新当前模型会话的人设 | [场景事件](../gateway/environment_events.py) |
| 导航偏好变化 | 环境事实静默更新上下文，不当作用户新话语 | [场景事件](../gateway/environment_events.py) |
| 温度提醒 | Service 观察条件从外进入内，事件经客户端送给前台 | [温度规则](../service/custom_skills/temperature_rules.py) |
| 自定义工作流 | 保存/加载定义，Agent 使用已有工具执行 | [技能工具](../service/tools/custom_skills/execute.py) |
| 长期记忆 | Gateway 的 MemoryProvider 管理，与座舱技能不同 | [记忆与技能面板](../client/memory_and_skills.py) |
| 评估 | 记录实际调用与状态，对照预期；各路径分别报告 | [评估流程](../bench/runner.py) |

这些是本地源码确认的职责关系。精简伪代码省略协议格式、并发与错误处理细节；
真正实现时使用源码，不把伪代码当作完整契约或已验证的运行结果。
