# 真实调用链与阅读断点

下面的箭头都对应学习版的真实函数或方法调用。先运行 `python3 main.py --demo --trace`，再按链路逐步跳转。
原项目对应的网络协议在学习版中用本地对象代替；原符号见 [源码对照表](source_map.md)。

## 启动：创建对象与连接依赖

```text
main.main → asyncio.run(async_main)
  → overview.run_demo
  → bootstrap.start.build_study_runtime
    → CockpitService → CockpitServiceServer
    → CockpitMcpTools → CockpitAgentTools → CockpitAgentExecutor → CockpitAgentServer
    → gateway.server.start_cockpit_gateway
      → create_backend_agent_host → create_gateway_application → GatewayApplication.start
    → CockpitApp.start
      → VoiceSessionController.start → GatewayClient.start → GatewayApplication.connect
        → RealtimeSessionRuntime + SessionTaskCoordinator
      → CockpitStateController.start → CockpitServiceServer.subscribe
```

[build_study_runtime](../bootstrap/start.py) 中每个构造函数都收到实际对象。
Service 在前后台之间共享，任务管理器由 Gateway 共享，每次客户端连接创建自己的前台会话。
这段装配最适合理解 Gateway：它把任务、后台适配和前台工具接给会话，并提供客户端接入入口。

## 普通聊天：不用后台任务

输入：`你好`。

```text
CockpitApp.send → VoiceSessionController.send_text → GatewayClient.send
  → RealtimeSessionRuntime.handle_client_event → handle_input
  → DemoRealtimeModel.plan → ModelReply
  → session.send → VoiceSessionController.on_event
```

`DemoRealtimeModel` 直接返回离线回复，没有创建 `TaskRecord`，没有修改 Service 状态。
原项目这里由实时语音模型产生回复，客户端负责接收和播放；学习版在终端展示文字。
建议断点：`RealtimeSessionRuntime.handle_input`。

## 前台工具：操作真实的模拟业务状态

输入：`空调调到24度`。

```text
handle_input → DemoRealtimeModel.plan → ToolCall(vehicle_temperature_control)
  → ToolCallHandler.handle → FrontendMcpToolSource.execute
  → CockpitMcpServer.call_tool → CockpitService.execute
  → ToolRegistry.execute → execute_vehicle
  → ToolContext.update → CockpitStateStore.update
  → ToolResult → DemoRealtimeModel.summarize → session.send
```

状态更新还有一条并行的观察链：

```text
CockpitStateStore.update → Signal.emit → CockpitServiceServer.subscribe 中的订阅
  → CockpitStateController.handle_event → apply_cockpit_state_update
  → CockpitApp.on_state → 导航上下文事件队列
```

客户端和模型看到的是同一个 Service 的业务结果。面板操作走 `CockpitStateController.execute` → `CockpitServiceServer.handle`，最终也调用同一个 `CockpitService.execute`。
未知工具或错误参数返回 `ToolResult(is_error=True)`；业务修改失败时不发布成功状态。
建议断点：[ToolCallHandler.handle](../framework_reference/frontend_session.py)、[CockpitService.execute](../service/cockpit_service.py)、[vehicle.execute](../service/tools/vehicle/execute.py)。

## 后台任务：回执、执行、通知分开

输入：`帮我买杯咖啡`。

```text
ToolCallHandler.handle(spawn_thinking) → TaskOperations.submit → TaskManager.create
  → 保存 queued 任务 → asyncio.create_task(_execute) → 立即返回 accepted 回执

TaskManager._execute → 获取当前用户的队列锁 → running
  → BackendWorkRuntime.run → A2ABackendAdapter.submit
  → CockpitAgentServer.submit → CockpitAgentExecutor.execute
  → run_cockpit_agent
    → DemoChatModel.complete → flashbuy(search)
    → CockpitAgentTools.call → CockpitMcpTools.call → 后台 MCP → Service
    → complete → flashbuy(add_to_cart)
    → complete → flashbuy(preview_order)
    → complete → 最终回复
  → TaskManager._finish → completed / notification=pending
  → SessionTaskCoordinator.on_event → refresh → _deliver
  → RealtimeSessionRuntime.present_task_result → 客户端收到后台结果
  → GatewayClient.playback_ack → TaskManager.mark_delivered
```

提交回执只表示接受工作；`completed` 表示后台执行完成；`delivered` 表示收到本地模拟播放确认。
静音时完成结果保持 `pending`；取消静音再投递。关闭当前会话不会取消已经接受的工作，关闭整个学习运行时会清理未完成任务。
默认客户端自动确认播放；设置 `app.voice.auto_play = False` 可以观察 `delivering` 状态，再手动调用 `playback_ack`。

`asyncio` 让模型等待和前台输入交错执行；后台任务在同一 Python 进程中，不是后台线程或独立服务进程。
学习版的服务边界对应原项目的 A2A/MCP，但这些类没有监听真实网络端口。
建议断点：[TaskManager._execute](../framework_reference/task_runtime.py)、[run_cockpit_agent](../agent/executor.py)、[SessionTaskCoordinator._deliver](../framework_reference/task_runtime.py)。

## 技能与环境事件

`custom_skill_create` 保存定义，不执行指令。
`运行上车准备技能` 调用 `custom_skill_load`，前台把工作流步骤重新规划为已有工具；后台步骤仍走 `spawn_thinking`。
温度提醒使用另一条链：

```text
车控更新 → CockpitStateStore → TemperatureSkillRules.observe
  → publish_activity → CockpitApp.on_activity → skill_triggered_event
  → VoiceSessionController.enqueue_environment → CockpitEnvironmentOutbox.flush
  → GatewayClient.request(client.event.publish)
  → RealtimeSessionRuntime.handle_client_event → skill_triggered → 客户端提醒
```

加载规则只建立基线；条件外进入条件内才触发，持续处于条件内不重复提醒。
提醒事件不执行工作流，也不创建后台任务。
导航偏好事件只更新 `DemoRealtimeModel.environment`；人设选择事件更新当前会话的 profile。

## 记忆与验证

`记住我喜欢晴天` → 前台 `memory_write` → Gateway 的 `MemoryProvider.apply`。
记忆面板通过 `GatewayMemoryController.load/remove` 访问同一 Provider；记忆按用户隔离，删除需要正确版本。
业务技能由 Service 管理，与 Gateway 记忆不同。

[tests/test_runtime.py](../tests/test_runtime.py) 验证以上主要路径及错误、取消、隔离和回执。
[bench/runner.py](../bench/runner.py) 用真实调用记录与权威状态评估四个离线规则模型用例；这不是原项目的大模型效果评测。
