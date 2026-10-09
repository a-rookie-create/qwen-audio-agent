# 对着代码读：从 main.py 走完整个智能座舱学习版

把这份笔记和 Python 代码并排打开。下面按一次运行的顺序带你跳转：读到一个调用，我们进去看它做什么；读到返回，就回到原来的调用处继续。链接指向当下该看的位置，不需要另外查目录或先读一套架构介绍。

这次以 `python3 main.py --demo` 为路线。先不用运行，跟着笔记在代码中走即可；遇到 `trace.record(...)` 可以先略过，它只是记下调用过程。各目录的 `__init__.py` 目前也只有说明，不会额外启动业务。

## 1. 打开 main.py，从文件底部开始

先打开 [main.py 的最后几行](../main.py#L57)。入口不是文件最上面的 `interactive()`，而是底部的 `if __name__ == '__main__'`。直接运行这个文件时，条件成立，执行 `main()`。

往上看 [main()](../main.py#L52)，只有 `asyncio.run(async_main())` 这一条核心语句。它启动事件循环，让 `async_main()` 这个异步函数真正运行。先把“事件循环”理解为驱动异步工作的运行环境，后面遇到后台任务时再看它怎样安排执行。

现在进入同文件的 [async_main()](../main.py#L30)。从 `parser` 读到 `args = parser.parse_args()`，这几行只解析命令行。接着顺着 `if/elif/else` 往下：我们给的是 `--demo`，所以既不走 interactive，也不走 benchmark，落在最后的 `await run_demo(args.trace)`。上面的 `--demo` 参数没有单独的判断分支，演示正是这个默认分支。

这时暂时不读 `interactive()`，沿 `run_demo` 的 import 打开 [overview.py 的 run_demo()](../overview.py#L7)。看到最前面的 `runtime = await build_study_runtime()`，就在这里停下。后面所有 `app.send(...)` 都依赖这个运行时，我们需要先把它创建出来。

## 2. 顺着 build_study_runtime，读对象怎样接在一起

跳到 [bootstrap/start.py 的 build_study_runtime()](../bootstrap/start.py#L36)，先确认它和 `class StudyRuntime` 一样顶格写着，因此它是类外的函数。右侧的 `-> StudyRuntime` 表示它返回这种对象，并不表示它属于这个类。

从 `env = load_cockpit_environment()` 开始读。进入 [bootstrap/environment.py](../bootstrap/environment.py#L7)，首句复制传入配置或 `os.environ`，下面的循环用于补充指定文件里的配置。我们这次没有传 `files`，循环不会进入，直接返回环境副本。回来继续看 `trace = TraceLog()`，再看 [study_support.py 的 TraceLog](../study_support.py#L45)：里面只有一个列表，`record()` 往列表加一条记录。现在知道它是日志容器就够了，回到装配函数。

读到这一行时，按括号从内向外看：

```python
service = CockpitServiceServer(CockpitService(trace, data_dir))
```

先进入 [service/cockpit_service.py 的构造方法](../service/cockpit_service.py#L14)。它创建状态 Store、技能存储、工具注册表、外部数据服务、活动 Signal 和温度规则。这里大部分代码是在保存依赖，尚未执行调空调或买咖啡。`self.skills.list`、`self.publish_activity` 没有加调用括号，是把方法作为回调交给规则对象。先记住这几个字段，真正使用时我们再回来展开。

回到装配处，外层 [CockpitServiceServer](../service/server.py#L8)只是把这个业务对象存进自己的 `self.service`。所以以后 `runtime.service.service` 的第一个 service 是入口包装对象，第二个 service 才是业务对象；这不是创建了两份业务状态。

继续读下一行 `tools = CockpitAgentTools(...)`。先看 `service.mcp('backend', cockpit_id)`，进入 [ServiceServer.mcp()](../service/server.py#L12)，它返回一个绑定后台工具面及车机 ID 的 MCP 对象，仍然引用刚才那一个 Service。再看 [agent/mcp_client.py](../agent/mcp_client.py#L6)，它把这个对象保存起来，`list()` 和 `call()` 都直接转交服务器。最后外层 [CockpitAgentTools](../agent/tools.py#L7)把业务工具和 `WebRetrieval` 放在一起。我们此时是在准备后台工具集合，还没调用其中任何工具。

往下看 `executor = CockpitAgentExecutor(...)`。没有传 model 时，会创建 `DemoChatModel`，参数是环境里的模拟延迟或默认 `0.02`。进入 [执行器的构造方法](../agent/executor.py#L58)，只需读到模型、工具、历史和活动执行字典被保存。它的 `execute()` 先不要展开，因为后台任务还没有提交。再进入 [start_cockpit_agent_server()](../agent/server.py#L29)，会发现只是创建 `CockpitAgentServer(executor)`，没有启动另一个进程。

现在回到 `gateway = start_cockpit_gateway(...)`，进入 [gateway/server.py](../gateway/server.py#L11)。第一条业务语句生成 config。点进 [gateway/profile_bundle.py](../gateway/profile_bundle.py#L22)，看到默认人设 `healer`、人设文本和前台工具名；`root` 没有传入，因此不写 JSON。读取人设的 [load_profile()](../gateway/environment_events.py#L18)先验证 ID，再读旁边的 Markdown 文件。读完返回 gateway/server.py。

下一句用 `A2ABackendAdapter` 包装 Agent，再交给 `create_backend_agent_host`。先看 [适配器构造方法](../framework_reference/backend_adapter.py#L17)，只是保存 server 和 trace；再看 [create_backend_agent_host](../framework_reference/backend_adapter.py#L38)，本版直接返回这个适配器。名字虽然叫 A2A，这里仍是本地对象之间的方法调用。

接着进入 [create_gateway_application()](../framework_reference/gateway_application.py#L63)，顺到上面的 [GatewayApplication.__init__](../framework_reference/gateway_application.py#L14)。从上到下读字段：`self.tasks` 保存任务，`self.backend` 负责连接后台执行，`self.operations` 把这两者接起来，`self.memory` 保存用户记忆，`self.sessions` 以后保存前台会话。先不展开各自的方法，我们马上会在实际输入里使用它们。

回到 gateway/server.py，末尾 `gateway.start()` 只打开 started 标记，没有创建会话。中间委派说明通过 [spawn_thinking_tool.py](../gateway/spawn_thinking_tool.py#L4)生成字符串并记日志，也没有开始后台工作。返回装配函数后，继续读 `app = CockpitApp(...)`。

进入 [client/app.py 的构造方法](../client/app.py#L13)。voice 拿到 Gateway，cockpit 拿到 Service；memory 和 skills 则分别拿到 Gateway 和 Service。`self.on_activity`、`self.on_state` 再次以函数对象的形式传入，等事件到来时才调用。现在构造都完成了，接下来那句 `app.start()` 才建立连接与订阅。

## 3. 读 app.start，看看客户端怎样第一次接上服务

先读 [CockpitApp.start()](../client/app.py#L23)，它先 `voice.start()`，再 `cockpit.start()`。沿第一句进入 [VoiceSessionController.start()](../client/voice_session.py#L22)，再进入 [GatewayClient.start()](../framework_reference/gateway_client.py#L16)，最后到 [GatewayApplication.connect()](../framework_reference/gateway_application.py#L31)。

connect 前几行检查 Gateway 已启动、该会话没有重复连接。然后创建 `RealtimeSessionRuntime`，将共享的 operations、memory、工具源，以及客户端回调 send 一起传进去。进入 [会话构造方法](../framework_reference/frontend_session.py#L89)，注意 `self.send = send` 对应的是客户端的 `on_event` 方法。以后在会话里调用 `self.send(...)`，会实际执行客户端的这个方法。

继续往下，模型和 ToolCallHandler 是这个新会话自己的对象。回来读 connect 的 `session.coordinator = SessionTaskCoordinator(...)`：它把当前会话接到共享任务事件上。先记住“后台完成后，靠这个协调器找到当前会话”，这里不急着读投递流程。connect 返回 session，GatewayClient 将它保存，voice 启动完成。

回到 app.start 的第二句，进入 [CockpitStateController.start()](../client/cockpit_state.py#L18)。这里把 `self.handle_event` 传给 ServiceServer.subscribe，并把返回值存成 `self.unsubscribe`。返回值是以后用来取消订阅的函数，不是订阅立即被取消了。

进入 [ServiceServer.subscribe()](../service/server.py#L42)，从第一句读起：它立即调用 listener，发送一个 snapshot。这里 listener 就是刚传入的 `handle_event`。快照由 [Store.snapshot()](../service/state_store.py#L36)提供：第一次按车机 ID 建立初始状态，再深拷贝返回。顺便往上读 [create_initial_cockpit_state()](../service/state_store.py#L8)，只要先认出 version 为 1、vehicle.acTemp 为 22、音乐未播放、购物车为空即可，其他字段等对应工具用到时再读。

回到客户端的 [handle_event()](../client/cockpit_state.py#L22)，这次走 snapshot 分支，保存 `self.state`，随后执行 `self.on_state(self.state)`。它会调用 App 的 on_state，准备把导航事实传给会话。这个异步转发先暂存为一个待读的分支，我们到温度提醒时会完整读它。

返回 ServiceServer.subscribe，余下几句接上后续状态、活动通知，并返回合并的取消函数。至此 app.start 结束。回到 bootstrap/start.py，`await app.voice.flush()` 等刚才快照引出的转发工作收尾，最后 `return StudyRuntime(...)`。

现在再看同文件上面的 [StudyRuntime](../bootstrap/start.py#L22)。`@dataclass` 自动生成初始化方法，五个字段就是这次装配的五个结果；构造它会把已有对象存起来，不会重新创建一套服务。文件底部的 start_four_processes 只是兼容旧名字，内部调用同一个装配函数，没有再启动四个进程。我们已经可以返回 overview.py，继续 `app = runtime.app`，然后读取第一条输入了。

## 4. 回到 overview.py，跟着“你好”读一条完整请求

回到 [overview.py 的第一条 app.send](../overview.py#L12)。先进入 [CockpitApp.send()](../client/app.py#L38)，它调用 voice.send_text；进入 [send_text()](../client/voice_session.py#L36)，文字被包装成 `{'type': 'input.message', 'text': text}`，再交给 [GatewayClient.send()](../framework_reference/gateway_client.py#L20)。它已经持有刚建立的 session，直接调用会话的 handle_client_event。

进入 [handle_client_event()](../framework_reference/frontend_session.py#L126)，这次 type 是 input.message，走第一条分支，调用 handle_input。接着进入同文件的 [handle_input()](../framework_reference/frontend_session.py#L100)，读到 `reply = self.model.plan(text)`，就往上进入 [DemoRealtimeModel.plan()](../framework_reference/frontend_session.py#L28)。

以“你好”为 text 从头走一遍：它不以“记住”开头，没有温度、音乐、导航、技能或后台目标，calls 一直为空，最终返回 `ModelReply('你好，我是离线座舱学习助手。')`。这里的模型是规则实现，不需要找一段隐藏的大模型请求。

现在打开 [study_support.py 的 ModelReply](../study_support.py#L39)。它有 content 和 tool_calls 两个字段，没给 tool_calls 时自动创建空列表。上面的 [ToolCall](../study_support.py#L31)则保存工具名、参数和调用 ID。先分清这两个对象：模型可以给文本，也可以给“请求执行工具”的描述。

回到 handle_input，`calls = list(reply.tool_calls)` 得到空列表，所以循环立即 break，results 也为空。构造 message 时因此使用 reply.content，task_ids 为空，随后执行 `self.send(message)`。

这次不要直接读 return，先沿 send 回到 [VoiceSessionController.on_event()](../client/voice_session.py#L25)。事件先加入 events；type 是 reply，又加入 messages；没有后台 task_id，不发送播放回执。回调结束，回到 handle_input 的 `return message`，结果沿几个 await 返回到 overview.py，print 取出 text 显示。

于是同一条 message 有两条出口：回调负责更新客户端消息列表，return 负责给当前调用者一个结果。只有回调在追加消息，return 没有再追加一次。到这里第一条输入已经走完，业务状态没有变，我们继续 overview.py 的下一行。

## 5. 对着“空调调到24度”读到真正的状态修改

第二条输入还有“播放晴天”，先跟空调这一段。重新进入前台 plan：温度正则匹配到 24，生成 `vehicle_temperature_control` 的 ToolCall，参数是 action=set、temperature=24.0、zone=all；随后音乐规则再追加 `music_play`。创建这两个对象时，空调与音乐状态都尚未变化。

回到 [handle_input 的循环](../framework_reference/frontend_session.py#L100)，这次 calls 不空。`pop(0)` 取出空调调用，交给 [ToolCallHandler.handle()](../framework_reference/frontend_session.py#L72)。按 call.name 读分支：既不是 spawn_thinking，也不是 memory_write，落到末尾的 `session.tools.execute(...)`。往上进入 [FrontendMcpToolSource.execute()](../framework_reference/frontend_session.py#L17)，再进入 [CockpitMcpServer.call_tool()](../service/mcp_server.py#L14)。

MCP 先确认工具在当前前台目录里，才进入 [CockpitService.execute()](../service/cockpit_service.py#L32)。这里正好用到装配时保存的几个字段：rules.prepare 为本车机建立一次温度观察器，ToolContext 带着车机 ID、Store、技能存储、数据服务和两个回调，最后 registry.execute 执行业务。先读 try/except：常见参数错误会变成 is_error=True 的结果，而不是成功提交一次状态。

进入 [ToolRegistry.execute()](../service/tools/registry.py#L42)，先按名称查 definition，再校验参数。沿 validate 看 required、类型、枚举与有限数值检查，留意 bool 被额外排除，因为 Python 中 bool 也是 int 的子类。回来读最后一行 `EXECUTORS[definition.domain](...)`：它从字典中取出 vehicle 对应的执行函数，再真正调用。

现在往上读同文件的 [构造方法](../service/tools/registry.py#L22)，就能解释 definition 从哪里来。初始化遍历六个领域，读取 manifest，将各工具名存成 ToolDefinition；surface-routing 决定前后台归属。可以打开 [vehicle/manifest.json](../service/tools/vehicle/manifest.json)，只定位 vehicle_temperature_control 的参数，不必把所有 Schema 都读完。再看 [ToolDefinition](../study_support.py#L11)，它只是保存这项目录数据。

沿路由进入 [service/tools/vehicle/execute.py](../service/tools/vehicle/execute.py#L14)。先取 before 快照，再看 temperature_control 分支。zone=all 从 ZONES 取出三个温度字段；检查范围后，changes 里存入三个 24.0 和 ac=True。读到末尾 `state = ctx.update('vehicle', changes)` 时停下：前面只是计算待修改内容，真正提交从这句开始。

进入 [ToolContext.update()](../service/tools/shared.py#L25)。代码很短，但这是你前面问到的 mutate 的实际来源：

```python
return self.store.update(self.cockpit_id, [domain], lambda state: state[domain].update(changes))
```

这次 domain 是 vehicle，changes 是刚算好的字典。lambda 是一个记住这些值的函数，它还没执行，而是作为第三个参数传给 Store。进入 [CockpitStateStore.update()](../service/state_store.py#L42)，参数上的 `Callable[[dict[str, Any]], None]` 描述“接收字典、返回 None 的函数”；方括号是类型标注，实际收到的 mutate 是刚才的 lambda。

从 `state = self.snapshot(cockpit_id)` 往下读：拿副本，调用 `mutate(state)`，这时 lambda 才合并 vehicle 里的变化。接着 version 加一，records 保存这个副本作为新状态，然后 events.emit。旧状态在调用修改函数时还没有被替换，修改成功以后才提交；第一次这条 vehicle 更新把版本从 1 变成 2。

读到 emit 时，我们先跟一下通知，等通知结束再回来读这个函数的 return。

## 6. 在 emit 这一行，读懂回调怎样让客户端同步

先进入 [Signal.emit()](../study_support.py#L71)。`tuple(self.listeners)` 是本次监听名单的元组，for 中的 listener 是名单里逐个取出的函数。执行 `listener(deepcopy(event))` 就是在调用这个函数，并给它独立的事件副本。异常被存进 errors，不会撤销 Store 已经保存的新温度。

为了知道名单里的函数是谁，往上读 [Signal.subscribe()](../study_support.py#L62)。append 把传入函数保存；里面 def unsubscribe 只是定义一个取消函数，末尾返回它。没有执行 unsubscribe()，所以不会刚添加就删除。以后客户端关闭时调用保存的取消函数，才真正删除 listener。emit 转元组则防止回调增删原列表影响这轮遍历。

再回 [Store.subscribe()](../service/state_store.py#L58)，这里注册的是 scoped 包装函数。它记住 cockpit_id 和原 listener，收到符合车机 ID 的事件才调用原 listener。本次原 listener 是客户端 handle_event，由启动时的 ServiceServer.subscribe 接上。

所以现在实际进入 [CockpitStateController.handle_event()](../client/cockpit_state.py#L22)。事件 type 是 state，调用 [apply_cockpit_state_update()](../client/projections.py#L8)。逐句读它：先取事件的新状态，未变领域复用客户端原对象，变化领域取新对象，version 取新值。这也说明 changed 应写 `['vehicle']`，而不是 `['acTemp']`，因为它按顶层领域判断。

handle_event 更新完 `self.state`，再调用 App.on_state，准备转发导航事实。温度规则的观察器也在监听同一个 Store，不过此时还没有创建提醒规则，不会发低温提醒。所有同步监听函数结束后，回到 Store.update，返回新状态的深拷贝。

现在顺着原来的调用返回：ToolContext.update → vehicle.execute。执行器用 [ctx.result()](../service/tools/shared.py#L30)包装结果；继续进 [tool_result()](../study_support.py#L82)，它带上当前版本，构造 [ToolResult](../study_support.py#L21)。ToolResult 的 content 是回复文本，data 是结构化结果，changed 和 state_version 是变化说明，is_error 默认 False。这个对象再一路返回前台 handle_input。

前台将结果加进 results，循环再取出 music_play。进入 [music/execute.py](../service/tools/music/execute.py#L9)，定位 play 分支：查演示曲库中的“晴天”，设置 playing=True 和 currentIndex，末尾同样调用 ctx.update。这第二次提交把版本变成 3，客户端也再次同步。

两个调用执行完，回到 handle_input 的 message 构造：results 不空，走 summarize，把两份真实结果文本用分号连接，再调用客户端回调并返回。回到 [overview.py 的两句温度打印](../overview.py#L15)，现在你知道为何 Service 温度和客户端温度都已经是 24。前台工具这条路至此闭合。

## 7. 回到“帮我买杯咖啡”，跟到后台真正执行

继续 [overview.py 的 receipt 这一行](../overview.py#L19)。输入沿刚读过的客户端路径进入 plan，这次咖啡关键字生成 spawn_thinking。回到 [ToolCallHandler.handle()](../framework_reference/frontend_session.py#L72)，终于进入先前略过的第一个分支：operations.submit 返回 task，Handler 把 task.id 放进 ToolResult.data，再由 handle_input 收集到回复的 task_ids。

先沿 submit 进去，打开 [TaskOperations.submit()](../framework_reference/task_runtime.py#L124)。内部 async def runner 只是定义“任务真正运行时做什么”，接着把 runner 传给 tasks.create。这个写法和刚才的 mutate 一样：先把函数交给别人，到了合适时机才被调用；区别是 runner 是异步函数，需要 await。

进入同文件的 [TaskManager.create()](../framework_reference/task_runtime.py#L44)，按顺序读：创建 TaskRecord，放进 tasks 字典，发 accepted 事件，create_task 安排 `_execute`，然后立即 return。现在先往上看 [TaskRecord](../framework_reference/task_runtime.py#L15)，认出 status 初值 queued，notification 初值 none，work 保存执行协程，finished 是等任务结束的 Event。数据类本身没有启动后台工作。

读到 create_task 不要把它当成“在这里等待完成”。当前调用会先把记录返回给前台，而 `_execute` 由事件循环继续驱动。沿 return 回到 Handler，再回 overview.py，receipt.text 是“后台工作已开始，你可以继续聊天”。它只说明工作被接受，下一句还能 `app.send('你好')`，因为我们尚未 await 整个咖啡流程。

现在读 [overview.py 的 wait_for_task](../overview.py#L23)，进入 [GatewayClient.wait_task()](../framework_reference/gateway_client.py#L37)，再进 [TaskManager.wait()](../framework_reference/task_runtime.py#L90)。这里真正等待 task.finished。等待期间事件循环可以推进刚才安排的后台协程，所以现在转去读 [TaskManager._execute()](../framework_reference/task_runtime.py#L53)。

它按 owner_id 取得锁，拿到锁才把 status 改成 running，然后 `await runner(task)`。同一用户的任务在这把锁前排队；queued 表示还未开始实际后台执行。回到 runner 的定义，顺着 `self.backend.run(...)` 进入 [BackendWorkRuntime.run()](../framework_reference/backend_adapter.py#L47)。

这里再调 `self.agent.submit(...)`。这个 agent 是装配时传入的 A2ABackendAdapter，进入它的 [submit()](../framework_reference/backend_adapter.py#L23)，任务对象被拆成 ID、目标和用户/会话上下文，传给 [CockpitAgentServer.submit()](../agent/server.py#L17)，再传给 [CockpitAgentExecutor.execute()](../agent/executor.py#L64)。中间这些层在转换接口和保存结果，还没有代替模型决定买什么。

若你往上看到 BackendPort 的 Protocol 和省略号，可以把它读成接口声明：具体提交工作已经由适配器实现了。它不要求你再补一段代码才能继续跑。

在执行器里，重点读 `self.history.messages(context_id)`、`create_task(run_cockpit_agent(...))`、`self.executions[task_id] = work` 和 `await asyncio.wait_for(work, timeout=600)`。它取旧历史，安排模型循环，保存取消时可定位的活动 Task，最多等待十分钟。最后 finally 一定移除活动记录。

先点进 [AgentHistory.messages()](../agent/agent_history.py#L11)：它将最近历史轮次里的 user/assistant 消息展开并深拷贝，给本次新目标预留一轮。后面的 append 只保存本次请求和最终回复，默认裁剪到 50 轮、最多 100 个上下文；它没有把整套购物车状态存进去。读完回到执行器，再进入 [run_cockpit_agent()](../agent/executor.py#L12)。

从函数开头读：先取得工具目录、生成允许工具名集合，再把历史和本次用户目标放进 messages。现在看 for 循环的第一句 `reply = await model.complete(...)`，沿它进入 [DemoChatModel.complete()](../agent/model.py#L19)。开头 sleep 模拟模型等待，这个 await 让前台也有机会执行。

第一轮 messages 末尾是用户目标，不是 tool，因此进入首轮选择；咖啡条件生成 `flashbuy(action='search', query='咖啡')`。回到 run_cockpit_agent，reply.tool_calls 不空，先记录 assistant 的工具请求，然后检查名称、预算，报告进度，执行 `await tools.call(...)`。报告“正在执行”是在调用前，不代表操作已成功。

进入 [CockpitAgentTools.call()](../agent/tools.py#L17)。flashbuy 不属于网页工具，转给 CockpitMcpTools.call，再到后台 MCP，最后回到刚读过的 Service/Registry。现在路由选择的是 [flashbuy/execute.py](../service/tools/flashbuy/execute.py#L12)。

在 flashbuy 里只读 search 分支：它从固定商品列表里找咖啡，把 results 和 status='searched' 存入 changes，末尾 ctx.update 保存新状态，再将完整 flashbuy 数据放进结果。于是模型下一轮能看见已经搜索出来的真实商品。

回到 run_cockpit_agent 的 `last = result`，继续读 messages.append：工具结果被记录为一条 tool 消息，tool_call_id 对应刚才的 call.id，额外的 result 字段让离线模型直接读取结构化结果。这里不是拿模型的口头承诺再问模型，而是把实际执行结果放回循环。

第二轮再次进入 DemoChatModel.complete，这次最后一条是 tool。它取 previous['result']，发现 flashbuy.status 是 searched 且有商品，于是生成 add_to_cart。顺到 flashbuy 的加购分支，商品价格来自固定目录，同商品旧项先移除再追加新数量，旧 preview 清空，状态改成 cart。

第三轮模型看到 cart，选择 preview_order。回到工具，复制购物车、算总价、保存 preview；第四轮模型看到 preview，返回“请明确确认是否下单”，没有 tool_calls。回到循环的 `if not reply.tool_calls`，这次真正返回最终 ToolResult。咖啡任务就在预览这里结束，order 仍是 None。

现在把循环余下的保护语句也顺着读完：最多十轮、三十二次实际工具调用，最后一轮不给新工具；未注册名字直接报错；预算用尽不继续操作。citations 按 URL 合并，咖啡没有引用，这个字典为空。执行结果成功返回 Executor 后，保存历史，再经 AgentServer、Adapter、BackendWorkRuntime 返回 runner，最终到 TaskManager._execute 的 `_finish(...)`。下面我们就从这里继续读结果如何回来。

## 8. 沿 _finish 看结果怎样回到客户端

进入 [TaskManager._finish()](../framework_reference/task_runtime.py#L69)。前两步保存 status/result，再发布 completed；然后成功或失败的任务设 notification='pending'，发布 notification.pending，最后 finished.set。status 讲的是工作是否结束，notification 讲的是结果是否通知到用户，两个字段分开变化。

这条 pending 事件会调用谁？回到同文件的 [SessionTaskCoordinator.__init__](../framework_reference/task_runtime.py#L139)，找 `tasks.events.subscribe(self.on_event)`。这是连接会话时注册的回调，pending 事件通过 Signal 调到 [on_event()](../framework_reference/task_runtime.py#L148)。

从 on_event 第一行读：取任务快照，核对 ownerId 和 sessionId，只接当前会话的任务。它先把事件发给客户端；客户端看到不是 reply，只存进 events，不作为聊天文字。遇到 notification.pending 时，再把 ID 加到 pending 集合并 refresh。

进入 [refresh()](../framework_reference/task_runtime.py#L158)。closed 或不能播报就返回；否则取 pending 任务，先改 notification='delivering'，再安排 `_deliver`。先改状态是为了避免重复 refresh 给同一任务再创建一次投递。work.add_done_callback 传入的是集合的 discard 方法，投递 Task 结束后才用这个 Task 作参数清理集合。

进入 [_deliver()](../framework_reference/task_runtime.py#L172)，再进入 [RealtimeSessionRuntime.present_task_result()](../framework_reference/frontend_session.py#L160)。它再检查会话未关闭、未静音，然后用 send 回调发送一条带 task_id、origin='background' 的 reply。此时工具已经执行完，这个函数只是呈现保存的结果。

再回客户端的 [on_event()](../client/voice_session.py#L25)，这次除了加入 messages，还命中 task_id 且 auto_play=True，于是发送 playback_ack。进入 [GatewayClient.playback_ack()](../framework_reference/gateway_client.py#L44)，再进入 [TaskManager.mark_delivered()](../framework_reference/task_runtime.py#L107)，通知状态才从 delivering 改为 delivered。本版这一步是模拟播放完成，没有真实扬声器。

回到 `_deliver`，看到已 delivered 就从 pending 移除。再回刚才等待的 GatewayClient.wait_task：它在等任务执行结束之后，还调用 coordinator.flush 等当前可安排的投递收尾。现在才返回 overview.py，所以打印出的任务状态是 completed，通知状态是 delivered。

读到这里可以顺手看 [VoiceSessionController.mute()](../client/voice_session.py#L70)，沿事件进入会话的 mute/unmute 分支：静音只是让协调器暂时不能播报，后台工具仍继续运行；取消静音会 refresh。若 auto_play 关掉，消息已到客户端也仍是 delivering，要手动 playback_ack。等任务执行结束与等播放确认不是同一件事。

再回 TaskManager._execute 的 except：普通异常变成 failed，CancelledError 单独变成 cancelled。沿 [TaskOperations.cancel()](../framework_reference/task_runtime.py#L131)读取消路径，它先验证任务归属，再通知 Agent 和 TaskManager 停止。TaskManager.cancel 对协程尚未开始的情形也补齐完成事件。已经执行成功的业务步骤不会因取消而回滚。这些分支读完，回到 overview.py 的下一条“确认下单”。

## 9. 从确认订单读到温度提醒，把前面的事件分支接完

回到 [overview.py 的 confirm](../overview.py#L28)，这句再次创建后台任务。沿 DemoChatModel.complete 的首轮选择，现在命中“确认下单”，直接生成 confirmed=True 的 confirm_order。再打开 [flashbuy.execute](../service/tools/flashbuy/execute.py#L12)，从 confirm_order 分支开始读。

先看已有 order 的提前返回，再看 preview 必须存在，接着看 confirmed 必须明确为 True。都通过以后才创建演示订单，清购物车和预览，提交 status='completed'。这里读取的是前一个任务在 Service 留下的购物状态，不是从上一个 TaskRecord 偷拿一个订单。读完返回 overview，等待新任务、打印订单 ID，此时业务版本是 7。

继续读 [overview.py 创建提醒的位置](../overview.py#L33)。这次入口变成 `app.cockpit.execute`，沿 [CockpitStateController.execute()](../client/cockpit_state.py#L34)进入 [ServiceServer.handle()](../service/server.py#L18)。定位 POST commands 分支，它最终仍调用 Service.execute。按钮或界面操作可以直接进 Service，不必先经过前台模型。

Registry 将 custom_skill_create 转给 [custom_skills/execute.py](../service/tools/custom_skills/execute.py#L6)。沿 create 分支进入 [CustomSkillStore.upsert()](../service/custom_skills/store.py#L27)，读名称、kind、existing 和 skill 的构造。同名沿用 ID，新技能生成新 ID；这次 kind 是 event，所以先 [normalize_temperature_trigger](../service/custom_skills/temperature_rules.py#L9)，验证温度范围并补默认观察字段 acTemp，再检查 reminder。全部通过才保存定义。

在技能 Store 内顺着 `_save()` 读到 [_path()](../service/custom_skills/store.py#L58)：未传 data_dir 时 root 为 None，这次不写文件；若指定目录，车机 ID 会编码成文件名，保存 JSON。再读 list/get，就能理解技能面板与模型工具为何都能按 ID 或名称读同一份定义。

返回技能执行器，下一句 `ctx.on_skills_changed()` 调用的是 Service 构造上下文时传入的 lambda，实际执行 [TemperatureSkillRules.refresh()](../service/custom_skills/temperature_rules.py#L37)。把 prepare 和 refresh 连着读：prepare 只为车机注册一次状态监听，refresh 加载事件技能并以当前状态建立 previous 基线。这里没有执行触发函数，所以“创建提醒”本身不发提醒，也没有把业务状态版本从 7 改成 8。

现在回到 overview 的 `app.send('空调调到19度')`。这次车控照刚才的路线提交状态，version 变成 8，Store.emit 调用已注册的温度观察器。进入 [TemperatureSkillRules.observe()](../service/custom_skills/temperature_rules.py#L43)，先取 before/after，再更新 previous，接着检查 changed 里有 vehicle，最后比较 old 和 new。

这里 old 是 24，new 是 19；默认条件下界为 16，上界为 20，所以 `not matches(old) and matches(new)` 成立。若原来已经 19，再改成 18，两个值都满足条件，就不会重复提醒。读 `self.on_triggered(...)`，它发的是一条带前后温度、提醒文字和事件 ID 的活动。

沿回调进入 [CockpitService.publish_activity()](../service/cockpit_service.py#L28)，再回 ServiceServer.subscribe 内的 on_activity 包装函数，按车机 ID 转给客户端 handle_event。这次 type 是 activity，handle_event 调 App.on_activity 后就 return，不更新客户端状态副本。

进入 [CockpitApp.on_activity()](../client/app.py#L28)，再进 [skill_triggered_event()](../client/projections.py#L27)。它筛掉非触发活动，把事件 ID、提醒及前后温度整理成客户端环境事件。返回 App，进入 [VoiceSessionController.enqueue_environment()](../client/voice_session.py#L43)。到这里终于展开启动时暂记的异步转发分支。

enqueue_environment 先把事件放进 environment，再 create_task(flush_environment)，把 Task 放进 pending_events。environment 保存“待发事件”，pending_events 保存“正在转发的异步任务”，两者不是同一份队列。随后 add_done_callback 把完成的 Task 从集合清掉，和后台结果投递的清理方式相同。

先读 [CockpitEnvironmentOutbox.enqueue()](../client/projections.py#L46)。提醒按 event_id 区分，context 则按事件名覆盖；队列超过 16 条淘汰最早条目。再读 [flush()](../client/projections.py#L56)：flushing 防止同时消费，会话可用才发送，过期的提醒丢弃，上下文事实不过期。await send 后确认 accepted 才删除；如果同一键在等待期间更新，身份判断会保留新值。

回到 [VoiceSessionController.flush_environment()](../client/voice_session.py#L51)，这里的 send lambda 实际调用 GatewayClient.request，is_ready lambda 检查连接和静音。进入 [GatewayClient.request()](../framework_reference/gateway_client.py#L26)，事件不是 task.create/cancel/get，落到 send，再进入会话 handle_client_event 的 client.event.publish 分支。

这个分支从 CLIENT_EVENT_DEFINITIONS 取 handler，调用它，拿到 delivery。现在进入 [gateway/environment_events.py 的 skill_triggered()](../gateway/environment_events.py#L39)，它再检查前后温度确实发生了条件转换，返回 mode='respond' 的 AgentDelivery。回到会话，走最后一支，直接把提醒作为 origin='environment' 的 reply 发给客户端，没有把提醒文字再交给 plan 执行工具。

返回 overview 的 `await app.voice.flush()`，它等刚才已创建的转发 Task 收尾，随后列表推导式从 messages 里找环境来源的回复，于是 print 读到“温度较低，请注意保暖”。这条提醒是在车辆状态已经更新之后，通过另一条异步链送来的。

现在补读一下此前多次经过的 [CockpitApp.on_state()](../client/app.py#L34)。它用 [navigation_preference_event()](../client/projections.py#L19)提取导航事实，也走同一转发队列，但 delivery_hint 是 context。进入 [navigation_preference_changed()](../gateway/environment_events.py#L31)，返回 mode='context'；会话只保存 model.environment，不发提醒。启动时初始快照引出的转发，走的正是这条路。至此启动处留下的阅读分支也接完了。

## 10. 回到已有函数，把工作流、记忆和其余工具读完

默认演示到这里已走过主要执行链。先回到 [custom_skills.execute](../service/tools/custom_skills/execute.py#L6)，读剩下的 list/load：它们都返回定义，没有执行指令。再回 [CustomSkillStore.upsert](../service/custom_skills/store.py#L27)的 workflow 分支，读到它要求 instructions，并禁止混入温度提醒字段。现在设想用户保存“上车准备”，instructions 是“空调调到25度，播放晴天”，创建时只保存这段文字。

沿前台 plan 的技能正则，以“运行上车准备技能”为 text 看一次：先请求 custom_skill_load，取得定义，再回 [handle_input()](../framework_reference/frontend_session.py#L100)的 load 结果判断。用户说了“运行”，kind 又是 workflow，因此重新 plan(skill['instructions'])，把得到的车控、音乐调用 extend 到现有 calls，继续同一个循环。这就是工作流的实际运行位置，不是存储类在创建时暗中调用了工具。八次调用的上限也覆盖展开后的请求。

再打开 [client/memory_and_skills.py](../client/memory_and_skills.py#L20)，读 CockpitSkillsController 的 list/load/remove。它们访问 ServiceServer 的技能路径，remove 最后走 [Service.delete_skill()](../service/cockpit_service.py#L53)，删除后刷新温度规则。把这条路与刚才模型使用的技能工具对照，能看出它们共用同一份技能定义。

还在 memory_and_skills.py，往上读 [GatewayMemoryController](../client/memory_and_skills.py#L6)，这次访问的却是 Gateway。用“记住我喜欢晴天”重新看前台 plan 第一支，得到 memory_write，Handler 将去掉“记住”的文字交给 memory.apply。进入 [MemoryProvider.apply()](../framework_reference/extension_ports.py#L19)：先拿文档副本，在副本里添加带 ID、version=1 的记忆，整批成功后才保存。

接着顺 remove 分支读：根据 ID 找当前记录，核对调用方带来的版本，再删除；任一步抛错都没执行末尾保存，所以前面处理的同批变更也不会部分提交。回到 GatewayMemoryController.remove，就能理解它为何把 item['version'] 一起发给 [GatewayApplication.memory_request()](../framework_reference/gateway_application.py#L47)。这份数据按 owner_id 保存，和按车机 ID 保存的技能、按会话保存的后台历史分开。

现在回到前台 plan 尚未跟过的“导航到西湖”和“天气”分支。它们照原有 Handler/MCP/Service 路径，分别进入 [navigation.execute](../service/tools/navigation/execute.py#L7)和 [weather.execute](../service/tools/weather/execute.py#L6)，不用再把包装层读一遍。

在导航执行器里，从 state/nav/changes 往下读。搜索地点直接返回，收藏、播报和视角各自准备变化；涉及路线的分支取目的地、复制途经点，再调用 services.plan_route。进入 [service/integrations/amap.py](../service/integrations/amap.py#L17)，看目的地与途经点校验，最后返回固定计算的演示距离/时长。回来读 status 的选择：路线查询保存 preview，开始导航才设 navigating；因此名称含 query 不等于完全不改状态。

在同一个适配文件里读 weather 和 search_places，就能理解天气执行器为何也会 ctx.update，把查询结果保存给面板。默认天气、位置、地点和路线是离线数据，工具读取这个接口，不在这里调用真实地图平台。vehicle_location() 是另一个可用辅助方法，默认车控位置查询直接读 Store 的 location。

回到 [music.execute](../service/tools/music/execute.py#L9)，先前只看了 play，现在把其余 elif 读完。pause/toggle 改播放开关，next/previous 用取模改变歌曲索引，音量夹在 0–11，静音单独保存 muted；收藏先复制 ID 列表再增删。每支都只算 changes，统一从末尾提交。再回 [vehicle.execute](../service/tools/vehicle/execute.py#L14)读剩下的 elif，也用这个办法：先找该分支往 changes 放了哪些字段，再看末尾一次 ctx.update。车窗合并旧字典以保留未选窗口，闪灯加次数而保留持续开关，充电分别改上限、电流和计划；你不必为每个工具重新理解一套状态机制。

为了读清重置入口，再回 [ServiceServer.handle()](../service/server.py#L18)的 reset 分支，沿它进入 [Store.reset()](../service/state_store.py#L65)。它直接换成初始状态，version 回到 1，changed 使用全部顶层键，然后仍通过 Signal 通知客户端。它没有去清 Gateway 的任务或记忆，因为那些不是 Store 保存的数据。

还有人设切换。进入 [VoiceSessionController.select_persona()](../client/voice_session.py#L65)，它发送 client.event.publish；再进 [select_assistant_profile()](../gateway/environment_events.py#L25)，加载指定 Markdown，返回 mode='handle'。回会话 handle_client_event 的第一种 delivery 分支，替换 profile_id/profile_text。这样就把三个 mode 都读过了：handle 改配置，context 存事实，respond 发提醒。默认规则模型保存人设文本，但没有依靠它生成不同风格的大模型回复。

最后补一条后台研究输入。把“研究一下智能座舱”代入 DemoChatModel.complete，首轮选 web_search。回 [CockpitAgentTools.call()](../agent/tools.py#L17)，这次终于命中网页分支，进入 [WebRetrieval.search()](../framework_reference/extension_ports.py#L55)，拿到固定演示引用；下一轮模型选择 fetch_url，读取固定页面，再形成回复。回 run_cockpit_agent 看 sources 的按 URL 合并，页面读取的 read=True 会补进同一条引用。

在 extension_ports.py 中紧挨着读 [KnowledgeProvider](../framework_reference/extension_ports.py#L37)，实现只是存文档和子串检索；装配函数没有创建它，所以不能把它画进刚才的默认输入链。再看 [DashScopeCockpitModel](../agent/model.py#L58)，它是可选适配器：清理内部消息字段、转换工具 Schema、调用注入客户端，再将响应还原成 ModelReply/ToolCall。默认创建的是 DemoChatModel，这里读接口转换即可，本次不需要真实客户端或密钥。

读完这些支线，回到 overview.py 的 finally，我们还有关闭过程与入口的两个模式没读。

## 11. 顺着 finally 退出，再回 main.py 补完两个模式

从 [overview.py 的 finally](../overview.py#L46)进入 [StudyRuntime.close()](../bootstrap/start.py#L29)。先 app.close，再 gateway.close。沿 [CockpitApp.close()](../client/app.py#L45)读，先执行 cockpit.close 中保存的 unsubscribe，随后 voice.close 等已创建的转发任务并停止会话。现在你终于看到前面返回的取消函数在哪里实际被调用了。

沿 [GatewayClient.stop()](../framework_reference/gateway_client.py#L48)进入 session.close，再进入 [SessionTaskCoordinator.close()](../framework_reference/task_runtime.py#L190)，它取消任务事件订阅和本会话投递，没有取消已经接受的后台工作。返回 StudyRuntime.close，下一句进入 [GatewayApplication.close()](../framework_reference/gateway_application.py#L55)，这里才继续调用 TaskManager.close，逐个取消未结束工作。单关会话和关整个运行时是两条不同的关闭路径。

现在回 [main.py 的 interactive()](../main.py#L10)。这次从头读就很快：同样装配 runtime，把一个打印 lambda 保存为 on_message，循环读取输入，再调用已经理解的 app.send。input 用 to_thread，以免等待终端输入挡住后台；exit、EOF 或异常后，finally 使用刚读过的 runtime.close。交互模式没有另一套业务实现。

再回 async_main 的 benchmark 分支，进入 [bench/runner.py 的 run_cases()](../bench/runner.py#L13)。每个 case 新建运行时，发送输入，有 task_id 就等待，再从 trace 取 Service 入口调用顺序，读取最终状态评分。进入 [bench/evaluator.py 的 score_trace()](../bench/evaluator.py#L12)，调用列表要求顺序和次数一致，get_path 把 vehicle.acTemp 这样的路径逐层取值，检查关注的状态字段。两个判断都通过才 passed，finally 同样关闭 runtime。

想用测试确认刚才的阅读，可以打开 [tests/test_runtime.py](../tests/test_runtime.py#L21)，先读 asyncSetUp/asyncTearDown，再挑 test_foreground_changes_state_and_updates_client 与 test_background_receipt_is_immediate_and_chat_can_continue。它们就是我们刚走的两条实际链，不需要先逐条阅读全部测试。收尾还检查 Signal.errors，防止观察回调报错却被遗漏。[test_imports.py](../tests/test_imports.py#L8)则遍历模块，转换路径为模块名并实际 import，检查引用可用。

到这里，从入口创建对象、首次连接、用户输入、状态变化、后台工作、环境提醒到关闭，你已经顺着代码走了一整圈。再看一个陌生方法时，可以先找到调用它的那一行，认出传入的数据和保存的对象，再读它最终返回或发出的事件；不用重新把全目录从上到下读一遍。

笔记对应源码提交 `343c478b137b6db59e4142a0591e11fc879cc8f6`，核对日期 2026-10-07。行号用于本次跳转，以后代码变化时按函数名定位。此前的[主题复盘资料](codebase-guide/README.md)留作读完后的查阅，不需要穿插进这次阅读。
