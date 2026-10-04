# 第 3 讲：实时对话与前台工具

[讲义入口](../README.md) · 上一讲：[启动与装配](../03-architecture-and-entrypoints.md) · 下一讲：[后台工作](tasks-permissions-and-delivery.md)

本讲回答：**用户的一次输入怎样得到回复？何时直接交流，何时使用工具？**

## 1. 先从用户行为读原文

| 顺序 | 原文 | 本次阅读重点 |
| --- | --- | --- |
| 1 | [对话与附件](../../guides/conversation.zh.md) | 语音、文字、发送、静音、附件与新会话分别意味着什么 |
| 2 | [详细架构：实时边界](../../architecture/deep-dive.zh.md#3-实时边界) | 前台可以直接处理哪些请求，工具如何随能力提供 |
| 3 | [前台核心 Prompt](../../../config/frontend-agent/PROMPT.md) | `Routing` 和 `Voice interaction`；这是中文规则，可以先于 JS 阅读 |

Prompt 告诉模型如何选择路径；工具 schema 描述如何调用；运行时执行真实校验。将这三层一起看，才知道“写了规则”和“实现了能力”各在哪里。

## 2. 讲义补充：连续对话是一段事件流

如果你熟悉 Python 的 `requests`，它容易给人“一次请求、一个完整返回值”的印象。这里更适合用 `asyncio` 长连接理解：输入音频不断到来，模型可能陆续返回转写、音频块或工具事件，客户端再排队播放。事件到达的时间、模型处理的时间和设备播放的时间并不相同。

沿[原文架构演示](../../voice-agent-architecture-presentation.zh.md)中“一个助手，运行在两种时间尺度上”和“结果交付必须服从双工会话状态”阅读，观察为什么系统需要分别记录用户说话、模型回复和客户端播放。

源码可沿这条 **static 定位路径** 追踪：

[Web 的 useRealtimeVoice](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/useRealtimeVoice.js#L203) → [客户端传输](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62) → [前台会话运行时](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-session-runtime.mjs#L56) → [RealtimeFrontend](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/realtime-provider.mjs#L111)。

不用一次读完这些文件。第一遍在会话运行时找输入处理、模型事件处理和向客户端发事件的三个位置；遇到回调查[语言桥梁](../01-python-to-javascript.md)。

## 3. 把“模型调用工具”与“工具执行”接起来

Python 类比：一个字典可以保存 `工具名 → 函数`，另一个字典描述函数参数。模型返回名称和参数后，程序查表、验证、调用，再把结果给模型。这能帮助你理解本项目的定义、注册表和 handler，但真实的去重、轮次与异步续答应以代码为准。

| 代码定位 | 对应阅读问题 |
| --- | --- |
| [frontendTools](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/frontend-tools.mjs#L109) | 当前模型会看到哪些工具定义？ |
| [FrontendToolRegistry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/frontend-tool-registry.mjs#L107) | 配置、能力和客户端条件怎样影响可用性？ |
| [ToolCallHandler.handle](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/tool-call-handler.mjs#L481) | 工具事件怎样被验证、派发和回填？ |

再读以下原文，给自己选两个真实例子：

- [联网搜索](../../guides/web-search.zh.md)的“结果与引用”：检索和读取网页可以组合，调用次数不自动决定转交后台。
- [清单与提醒](../../guides/notes-reminders.zh.md)：清单条目、到点播报、定时执行要区分。
- [前台 MCP](../../reference/frontend-mcp.zh.md)和[OpenAPI](../../reference/frontend-openapi.zh.md)：外部工具通过显式配置进入工具面；详细白名单和权限边界读原文。

前台 MCP 和后台 Agent 自带的 MCP 是不同接入位置。比较[前台 MCP 原文](../../reference/frontend-mcp.zh.md)与[后台 Skills 指南](../../guides/skills.zh.md)，先问“这个服务被谁调用”，不要只看协议名称。

## 4. 媒体和供应商差异去哪里看

[视觉输入](../../guides/vision.zh.md)已经完整区分附件、摄像头帧和 X-Omni 按需采集，本讲不重新列一份限制表。对照其“客户端限制”，解释为什么有摄像头权限仍不足以证明当前组合支持视觉工具。

配置现成模型读[语音前台设置](../../configuration/frontend.zh.md)和所选服务文档，入口在[原文地图](../source-reading-map.md#3-对话媒体与语音模型)。想理解协议转换再读[自定义 Realtime Provider](../../voice-frontends/custom-provider.zh.md)：关注 `encodeOutgoing` / `normalizeIncoming`，以及“上下文写入”和“触发回复”的区别。

Provider 可类比 Python 中包装外部 SDK 的对象。统一方法方便上层调用；原生工具续答、确认事件与输入能力仍有差异，必须在 Adapter 内声明和处理。完整方法与测试规则在原文中。

## 5. 本讲检查题

1. 普通对话是否必须创建后台 Task？
2. 工具定义、可用性与 handler 分别解决什么问题？
3. 前台搜索为什么不要求后台 Agent？
4. 图片附件与实时摄像头帧为何不能当成同一输入？
5. 模型生成结束为什么不等于设备播放结束？

用上面的原文回答前四题；第五题从架构演示和[下一讲的结果交付](tasks-permissions-and-delivery.md#4-讲义补充完成与交付是两条状态轴)继续理解。
