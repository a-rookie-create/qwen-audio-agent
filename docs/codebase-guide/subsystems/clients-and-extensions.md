# 第 7 讲：客户端、扩展与场景

[讲义入口](../README.md) · 上一讲：[状态与恢复](../data/state-and-persistence.md) · 下一讲：[运行与验证](../operations/runtime-and-tests.md)

本讲回答：**如果换一项能力，应从哪个边界接入？只会 Python 可以怎样参与？**

## 1. 先确定你要替换的是什么

先读[扩展总览](../../extensions.zh.md)。原文已经列出模型、工具、知识、后台、人设/记忆、客户端和桌面外观的入口；以这份原文作选择表。

| 学习问题 | 原文入口 | 本次关注 |
| --- | --- | --- |
| 给用户换一个界面或设备 | [Gateway 契约](../../contract.zh.md)、[客户端协议](../../gateway-protocol.zh.md) | 公开入口与客户端职责；握手、能力、事件和动作 |
| 换实时语音服务 | [Realtime Provider](../../voice-frontends/custom-provider.zh.md) | 原生协议转换、模型会话与能力声明 |
| 给前台增加 Python 服务能力 | [MCP](../../reference/frontend-mcp.zh.md)、[OpenAPI](../../reference/frontend-openapi.zh.md) | 显式暴露操作、schema、调用与服务自己的鉴权/确认 |
| 换办事 Agent | [接入新后台](../../backends/extend.zh.md)、[Backend SDK](../../reference/backend-adapter-sdk.zh.md) | 四种接入路径与通用工作契约 |
| 换知识/记忆实现 | [Knowledge Provider](../../reference/knowledge.zh.md)、[Memory Provider](../../reference/memory-provider.zh.md) | Node 接口与外部服务之间的转换 |
| 打包前台体验或换外观 | [Frontend Profile](../../reference/frontend-profile.zh.md)、[皮肤规范](../../desktop/pet-skin-spec.zh.md) | 配置组合、引用与外观资源的边界 |

这里是原文的学习分组，不增加新的插件协议。完整接口与配置由对应原文维护。

## 2. 讲义补充：Python 服务与 Node 接口之间需要桥接

你会 Python，已有检索、记忆或业务 API 可以继续用 Python 实现。关键先判断它提供的是“一次前台工具动作”“知识检索”“记忆生命周期”还是“持续工作的执行服务”。这些能力的结果、状态和取消要求不同。

可借助两份项目原文理解跨语言边界：

- [LightRAG 示例 README](../../../examples/lightrag/README_ZH.md)的“架构”：外部知识服务负责索引和算法，Node Provider 转换请求与返回值。
- [VoiceMem 示例 README](../../../examples/voicemem/README_ZH.md)的“架构”：Python Sidecar 执行记忆能力，框架连接器提供需要的快照和生命周期接口。

这是服务/进程之间的协作，不是把 Python 对象直接传入 JavaScript 工厂。若用 Python HTTP API 接前台工具，可以从 OpenAPI 原文了解如何公开选定操作；若要完整后台 Task 生命周期，再读 Backend SDK。讲义不另外发明跨语言接口。

## 3. 客户端协议：把“消息”与“环境动作”分清

按[客户端协议](../../gateway-protocol.zh.md)先读第 1～3 节，再按需要读第 5 节中的输入、环境事件、客户端工具、命令与回执。原文已有完整协议面，第一次不需要记住全部事件名。

Python 类比：WebSocket 连接建立只是通信通道出现；应用仍要交换版本、能力和身份。`session.ready` 与上游模型连接成功是不同事实。原文健康契约版本与 GCP 线协议版本也用于不同层面，不能只凭包版本号推断所有能力。

Client Event 可以理解为“环境发生了什么”；Client Action 是“请环境做什么，并回报结果”。Python 中发布一个事件与调用一个等待结果的函数也不同。对照协议第 5～7 节，把摄像头状态、一次客户端动作与前台休眠分别放到正确位置。

源码验证入口：[GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63)、[共享状态 reducer](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-state.mjs#L29)、[客户端命令运行时](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/client/client-command-runtime.mjs#L39)。它们接到应用级服务，不让 UI 直接操作服务端内部对象。

## 4. 用原有客户端和示例检验整体理解

客户端的完整使用与限制读[桌面](../../desktop/overview.zh.md)、[WebUI](../../getting-started/webui.zh.md)、[TUI](../../getting-started/tui.zh.md)、[手机](../../getting-started/mobile.zh.md)。远程部署读[连接与配对](../../operations/remote-access.zh.md)；媒体接入变化读[WebRTC](../../gateway-webrtc-client.zh.md)。区分客户端到 Gateway 的媒体链路与 Gateway 到模型的原生协议。

再从[原项目示例索引](../../scenarios/index.zh.md)选一个场景，按以下三个问题阅读它的原 README：

1. 复用了哪些通用能力？
2. 增加了哪些业务工具、领域状态、客户端事件或 Provider？
3. 哪些能力与验证结果只属于这份示例？

所有现有场景入口，包括数字人、座舱、客服、视觉、硬件、外部记忆和知识，都汇总在[原文地图](../source-reading-map.md#7-场景看通用边界怎样支持不同业务)。以原文声明的范围读示例；例如硬件半双工不能概括成所有客户端都具有相同体验。

## 5. 本讲检查题

1. Python 检索服务、一次业务 API 和持续执行服务，分别可接哪类接口？
2. Realtime Provider、BackendPort 与 GCP 为什么不能互换？
3. Socket 已连接为什么不等于模型已就绪？
4. 阅读一个业务示例时，怎样把框架职责与业务规则分开？

回扩展总览、对应接口原文和所选示例回答。实现时再查[语言桥梁](../01-python-to-javascript.md)与[代码索引](../key-code-index.md)。
