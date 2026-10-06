# 哪些能换成 Python

本地仓库的公开装配与客户端 SDK 是 JavaScript 模块，未发现对应 Python 装配 SDK。
本学习副本的类、函数与伪操作只表达思想，不会让 Python 直接调用 .mjs 导出的函数。

| 部分 | Python 接入方式 | 必须保留的契约 |
|---|---|---|
| 自定义客户端 | 实现 GCP 客户端，连接现有 JS Gateway | 握手、认证、能力协商、输入/输出、请求关联、回执与恢复 |
| 座舱后台 Agent | 用 Python 写模型循环，暴露兼容 A2A 服务 | Agent Card、消息、流式状态、artifact、取消、context 连续性 |
| 座舱业务 Service | 用 Python 实现业务状态和工具，暴露 MCP 与 HTTP/SSE | 两个 MCP 工具面、工具名/Schema、返回结构、UI 接口与 SSE |
| 后台模型调用 | 用 Python 的模型客户端调用兼容模型接口 | messages、tool_calls、tool results、供应商参数与取消 |
| Gateway 宿主装配 | 保留现有 JS 入口，通过 URL/配置接入 Python Agent/Service | 公开 JS API 在 Node 进程内使用 |
| Memory/Knowledge 等扩展 | 保留 JS Provider 适配壳，按需连接 Python 服务 | Memory list 同步快照等完整接口，不能直接注入 Python 对象 |
| 网页检索复用 | Python 重新实现，或明确增加 JS ↔ Python 协议桥接 | 现有 createWebRetrieval 是进程内 JS API，没有自动 HTTP 入口 |
| 浏览器 React 页面 | 继续用 JS，或另选 Python 客户端并重新实现 UI/I/O | Python 服务端不能直接替代浏览器的 React、Web Audio 与 3D |

最小实际迁移路线可以是：保留 client + Gateway，将 agent 换成 Python。
现有 Gateway 仍按同一 Agent Card URL 联系后台，业务工具也继续走原 /mcp/backend。
这样可以先迁移熟悉的模型工具循环，后续再单独迁移 Service。
这是接口分析建议，本次没有执行实际迁移。

若把整个 Gateway 改写成 Python，还要实现 GCP 服务端、实时供应商适配、
音频生命周期、任务存储/恢复/授权、投递重试等，属于框架移植。
“换一种语言连接服务”与“换一种语言实现服务器”工作量不同。

## 一个重要例子

```python
# 跨进程：可由 Python 实现，Gateway 内部语言无关。
await python_client.connect("ws://gateway/api/realtime")
await python_agent.serve_a2a(agent_card=..., executor=...)

# 进程内 JS 装配：不是 Python import 可直接调用的对象。
application = createGatewayApplication(...)
```

上面的名字仅用于说明边界；没有承诺存在某个名为 python_client 的官方库。
实施时必须按当前协议与实际选定 SDK 编写和验证。

依据：[公开能力](framework_api.md)、[源码对照](source_map.md)。
