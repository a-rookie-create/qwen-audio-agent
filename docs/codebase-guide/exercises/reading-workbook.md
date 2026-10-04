# 练习与答案：把伴读转成自己的理解

[返回伴读入口](../README.md)

## 1. 每次学习留下三种产物

每完成一个[历史阶段](../02-history-reading-route.md)，用你自己的话保存：一句“这个阶段解决了什么”；一条带文件 / 符号的调用链；一个已验证的失败或分支。不要以读过文件数量判断进度。

可以直接使用这个模板：

```text
阶段 / 快照：
我已理解的行为：
输入 → 入口 → 状态变化 → 输出：
关键文件与符号：
一个正常分支：
一个失败或并发分支：
测试依据：
尚未确认的问题：
```

## 2. 四轮阅读安排

| 轮次 | 内容 | 完成标准 |
| --- | --- | --- |
| 第一轮 | 系统地图、JS 桥梁、历史 1～4 | 找到启动与工具入口，区分客户端和模型 |
| 第二轮 | 历史 5～8、Task 流程 | 能解释受理、delegated、权限、取消与投递 |
| 第三轮 | 历史 9～11、记忆知识、客户端、持久化 | 能指出每类状态的权威与替换接口 |
| 第四轮 | 历史 12、一个示例、代码索引 | 画出完整业务链，并标明哪些行为由示例承担 |

每轮可以拆成多次，每次 30～60 分钟。遇到 JS 不熟悉的表达式，先回桥梁查对应语法，再回原来的调用链，不必临时展开成一门完整语言课程。

## 3. 先运行 Python 教学模型

在仓库根目录：

```bash
python3 docs/codebase-guide/exercises/nonblocking_demo.py
```

只需要 Python 3.10+ 标准库，不连接模型、网络或 Gateway，不读写用户配置。它展示三个独立事实：Task 已受理；后台结果已完成但用户仍在说话；音频开始播放后通知才标已交付。

代码是 **teaching**：用一个 worker 和模拟延迟刻画核心因果关系。它省略真实 Provider、工具循环、授权、owner 隔离、delegated 并行、持久化和重连；不是项目移植版，也不替代源码测试。

运行前预测输出顺序，再检查：`accepted` 应先于执行完成；后台执行期间仍有对话输出；结果完成后，要等用户空闲才生成播报；模拟生成完成时通知仍为 delivering，模拟播放开始后才 delivered。具体时间只是演示，不是产品延迟数据。

## 4. 十个源码检查题

先回答，再看后面的答案和定位。

1. `spawn_thinking` 创建 Task 后是否等待 BackendPort.submit 完成，才给回执？
2. TaskManager 最大 owner 并发与后台 `laneLimit: 1` 是同一限制吗？
3. `delegated` 是否意味着 Task 已完成？为什么还能启动下一项入口？
4. 后台输出“用户已经允许”能否自己制造一个真实权限决定？
5. pending input 显示 `input_required` 时，内部 status 必须是同名字符串吗？
6. 普通音频播报中的模型 `response.done` 能否直接把结果通知标为 delivered？
7. 前台断连是否必须把已受理 Task 取消？
8. 直接把远程 HTTP 调用放进 MemoryProvider.list 是否符合契约？
9. 默认本机 KnowledgeProvider 用的是向量检索吗？
10. `TaskManager` 构造器默认保留三天，就能断言正常 Gateway 也默认三天吗？

## 5. 参考答案与依据

1. **不等待最终完成。** [TaskManager.create / #create](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L428) 返回快照并安排 drain；[AgentTaskRuntime.executeSpawnThinkingToolCall](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L195) 给 accepted / duplicate 回执。受理路径仍可能等待工具输出或少见转写 fallback。
2. **不同。** TaskManager 调度配额控制可运行项，[TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57) 另设后台 owner lane。配置还会覆盖对象默认值。
3. **未完成。** [TaskManager.start](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L623) 在 Adapter 的真实委派事件到达后释放通道，持续保持 Task 生命周期。
4. **不能。** 权限来自规范请求、关联与用户答复，再经 [PermissionPolicy](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/permission-policy.mjs#L9) 和 [TaskOperations](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L34) 处理；普通文本不等于授权事件。
5. **不必。** [publicWorkState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-state.mjs#L117) 从 inputRequest / authorization 等投影 workState，内部 status 独立。
6. **普通音频路径不能。** 纯文字完成和主动打断的消费确认另见 Task 流程第 9 节。[AnnouncementManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-manager.mjs#L66) 等客户端开始播放的事实；后台 completed 也不是 delivered。
7. **不应仅因断连就取消。** [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12) 关闭释放订阅与 claim；显式工作取消走 [TaskManager.cancel](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L855) / TaskOperations.cancel。
8. **不符合同步快照要求。** [assertMemoryProvider / provider contract](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/memory/provider.mjs#L76) 明确 list 的实时契约；远程数据要经有界本地快照或其他异步接口。
9. **不是。** [LocalKnowledgeProvider](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/knowledge/providers/local/provider.mjs#L104) 使用文本分块、词项 / 元数据匹配和评分；外部 Provider 可以采用别的检索算法。
10. **不能。** [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63) 传入 [config](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/core/config.mjs#L234) 的值；当前配置缺省是一天。类默认值、注释与装配后的行为要一起核对。

## 6. 三个不用改生产代码的深入任务

**任务 A：历史前后对照。** 查看 `866d03a` 的 stat，再比较父提交与该提交的旧 coordinator / 新 BackendWorkRuntime。写下哪些行为退出通用层，哪些仍由 TaskManager 管理。验收：不能把当前编排运行时画成必须调用的独立协调模型。

**任务 B：给一项工作画双状态轴。** 横轴按顺序记录 accepted、running、completed、模型生成、playback.started；纵向分别写 status 和 notificationStatus。验收：能画出 completed + pending / delivering 的合理组合。

**任务 C：用 Python 背景读 LightRAG。** 只读示例 Gateway、Node Provider 和独立服务配置，画出检索 request / context / result 的对应关系。验收：能指出 trusted owner、取消、结果归一化属于 Adapter / Runtime，向量与图算法属于外部知识服务。

## 7. 最终自测：能独立解释项目了吗

试着不用伴读正文，用一页纸回答：系统解决什么；逻辑角色与进程怎样区分；一次工具调用在哪里开始；一项 Task 谁拥有；权限从哪里来；为什么执行完成不等于结果交付；换模型、后台和知识库分别改哪层；重启能恢复什么。

如果其中某题答不清，回[代码索引](../key-code-index.md)找对应符号和一个代表测试，重新追一条具体行为即可。完整理解不要求记住全部文件，更要求能用证据定位并解释行为。
