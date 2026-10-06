# 框架支持什么，接口怎么调用

框架主体在 server/src；协议和客户端 SDK 还在 shared，
默认前台提示词在 config。package.json 的 exports 是外部应用可 import 的公开入口。

“服务”需要分三种理解：

1. **进程内装配 API**：JS 应用 import 后创建对象，把依赖传进去。
2. **运行中的网络接口**：其他进程通过 GCP、HTTP、A2A、MCP 接入。
3. **扩展契约**：实现指定的方法/配置，由 Gateway 在启动时接入。

它们并非每项都对应一个独立服务进程。服务端某个 class 也不自动是公开 SDK。

## 能力目录

| 能力 | 主要实现 | 公开入口 / 使用方式 |
|---|---|---|
| Gateway 组装、启动、关闭 | server/src/app/ | qwen-audio-agent/gateway-application 的 createGatewayApplication |
| 客户端语音、文本、图片/文件、会话与恢复 | transport/、voice/、shared/protocol/ | GCP；JS 客户端使用 gateway-client-sdk 的 GatewayClient |
| 前台上下文、实时模型、音频与播报 | voice/、conversation/ | 通过 Gateway 会话使用；实时供应商通过 realtime-provider 扩展 |
| 前台内置工具、MCP/OpenAPI 工具 | frontend/tools/ | 工具目录、执行器、配置/Profile；不是每个内部处理器都公开导出 |
| 后台任务提交、排队、取消、权限、补充输入、定时任务 | task/、orchestration/ | GCP task.create/get/list/cancel、permission.respond、task.input.respond；宿主注入 TaskOperations |
| 后台接入与启动 | backend/、process/ | backend-adapter-sdk 的 BackendPort/Host；A2A 适配器；ACP 与 driver 接入 |
| 长期记忆与偏好学习 | memory/ | memory-provider；前台工具；Gateway GET/PATCH /api/memory |
| 知识库检索与可选入库/管理 | knowledge/ | knowledge-provider；前台工具；启用管理时使用 /api/domain 相关路由 |
| 搜索、网页读取与来源信息 | frontend/retrieval/ | web-retrieval 的 createWebRetrieval；返回 search/fetchUrl 等进程内能力 |
| 场景事件、人设刷新、消息投递 | client/、delivery/ | client-events、agent-delivery；客户端用 client.event.publish |
| 客户端动作与在线/休眠状态 | client/、shared/gateway/ | client-actions、GCP actions/presence；按协商能力启用 |
| 任务查询、时间线、会话日志、回放、历史 | task/、session/、conversation/ | Gateway HTTP 控制面和 GCP history/replay |
| 认证、设备配对、访问密钥、健康检查 | access/、app/gateway-http-routes.mjs | /api/access/*、/api/health；相关客户端辅助导出 |
| 可选 WebRTC 传输 | transport/webrtc/、packages/webrtc/ | 扩展包与客户端能力；仍复用 Gateway 生命周期 |

具体可用性受配置、Provider、后台健康状态及能力协商影响。表中“支持”不表示
每个座舱实例都配置并调用了所有能力，也不把内部源码当成稳定公开 API。

## 像 SDK 那样调用的部分

```python
# Python 风格示意；真实公开入口是 JavaScript import。
adapter = create_a2a_backend_adapter(agent_card_url=...)
host = create_backend_agent_host(adapter)
application = create_gateway_application(agent=host, auto_start=False, ...)
application.start(host=..., port=...)
```

这些是框架的宿主/装配 API。它们创建并启动应用，在同一个 Node.js 进程里接线。
GatewayClient 是客户端 SDK，帮助应用连接已经启动的 Gateway。
createWebRetrieval 则可独立供 Agent 使用，调用时才执行网络检索。

因此可以把公开包导出理解为一组 JavaScript SDK 能力，
整个 qwen-audio-agent 还包含运行时、服务器与客户端产品。
不能从“有 SDK 接口”推出“只有一个远程模型调用函数”。

## 网络接口举例

| 接口 | 用途 | 调用方 |
|---|---|---|
| WS /api/realtime | GCP 握手、输入、回复、任务与场景事件 | 座舱 client |
| GCP task.create / task.cancel | 显式任务操作 | 有协商能力的客户端 |
| GET /api/tasks、GET /api/tasks/:id | HTTP 查询任务 | 管理/客户端控制面 |
| DELETE /api/tasks/:id | HTTP 取消任务 | 有访问身份的调用方 |
| GET/PATCH /api/memory | 查询与修改记忆 | 座舱 Memory 面板 |
| GET /api/conversations/:sessionId/messages | 查询历史 | 客户端控制面 |
| GET /api/sessions/:sessionId/events、replay | 日志与回放 | 调试/恢复入口 |
| A2A Agent Card 和消息/任务接口 | Gateway 联系后台 | A2A Adapter |

GCP 请求需要真实 envelope、event_id、握手与能力协商；不能只复制一条音频字典
就宣称实现了协议。学习版 GatewayClient 把这些细节显式留为占位。

## smart-cockpit 实际使用哪些

| 场景位置 | 框架能力 | 使用性质 |
|---|---|---|
| gateway/server.mjs | createGatewayApplication | JS 公开装配 API |
| gateway/server.mjs | createA2ABackendAdapter、createBackendAgentHost | JS 接入 API + 跨进程 A2A |
| gateway/profile-bundle.mjs | 前台 Profile、MCP 配置 | 场景生成配置，框架读取并接入 |
| gateway/environment-events.mjs | createAgentDelivery 与自定义客户端事件 | JS 注册事件，GCP 客户端发布 |
| gateway/assistant/event.mjs | 同会话人设更新 | 注册 handler，调用框架提供的 effects |
| client/useVoiceSession.js | GatewayClient、协议/事件定义 | JS SDK + GCP；输入、播放回执、事件、恢复 |
| client/useGatewayMemory.js | GET/PATCH /api/memory | HTTP；记忆由框架模块管理 |
| agent/tools.mjs | createWebRetrieval | 后台进程内复用框架的网页能力 |
| Gateway 内部 | 实时 Provider、任务调度、通知、上下文、会话日志等 | createGatewayApplication 装配后间接使用 |

座舱 Service 的车辆/导航/音乐/天气/闪购/自定义技能是场景业务，
它使用 MCP 暴露工具、使用 HTTP/SSE 驱动 UI，不是框架内置车辆服务。
后台模型调用用的是 openai 与 DashScope；A2A/MCP SDK 来自各自协议包。
本次未发现座舱配置专用 KnowledgeProvider 或依赖框架自带 web/ 页面：
它使用自己的 client/，知识库是框架可选能力。

默认工具路由：前台 37 个，后台 1 个 flashbuy。
后台额外组合 web_search/fetch_url，按检索能力是否可用提供，不计入 Service 的 38 个。

## 契约怎样理解

BackendPort 必需方法：describe/start/health/submit/status/cancel/
respondAuthorization/respondInput/subscribe/close。它是代码接口，适配器内部才处理协议。

MemoryProvider 必需 describe/list/apply；list 是实时提示词用的同步快照。
KnowledgeProvider 必需 describe/retrieve，管理方法 ingest/list/remove 可选。
Realtime Provider 是供应商连接和事件转换的注册对象；不同契约不能混成一个服务。

所有声明均为 static；准确符号与行号见 [源码对照](source_map.md)。
