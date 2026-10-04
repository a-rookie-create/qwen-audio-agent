# 01：Python 使用者的 JavaScript 阅读桥梁

[返回伴读入口](README.md) · 下一章：[历史阅读路线](02-history-reading-route.md)

你的目标首先是看懂项目控制流。下面只覆盖本项目高频语法；Python 代码是 **teaching** 类比，不能直接替换 JavaScript 实现。

## 1. 文件、运行环境与依赖

| 项目中看到的东西 | 如何理解 |
| --- | --- |
| `.mjs` | 明确使用 ES Modules 的 JavaScript，服务端核心大量采用它 |
| `.js` | JavaScript；所属包的 `type: module` 或构建配置决定其模块处理方式 |
| `.cjs` | CommonJS 模块，常见于 Electron 等兼容入口 |
| `.jsx` | 包含 JSX 界面描述的 JavaScript，主要用于 React 客户端 |
| Node.js | 运行服务端 JavaScript 的环境，可访问文件、网络、子进程 |
| 浏览器 | 运行 Web 客户端，提供 DOM、麦克风和 Web Audio 等 API |
| Electron | 桌面宿主，有主进程、渲染进程和 preload 边界 |
| `package.json` | 包元数据、依赖、脚本、工作区与公开导出；相当于 Python 多份项目配置的一部分职责 |
| `package-lock.json` / `npm ci` | 锁定依赖 / 按锁文件安装；类比固定依赖后的可复现安装 |

本项目是多个 npm workspace 加独立示例的仓库。`npm run dev`、`npm run gateway` 等最终执行什么，先看根目录和各 workspace 的 `package.json`。所有包不是同时参与每一条链路。

证据：[根包配置](../../package.json)、[server 包](../../server/package.json)、[web 包](../../web/package.json)、[desktop 包](../../desktop/package.json)。

## 2. 导入、导出与模块执行

实际代码见 [bootstrap module](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/bootstrap.mjs#L1)：

```javascript
import { createGatewayApplication } from './gateway-application.mjs'
const application = createGatewayApplication()
export const server = application.server
```

可以先类比：

```python
from gateway_application import create_gateway_application
application = create_gateway_application()
server = application.server
```

花括号表示命名导入。`export` 让别的模块能导入该名字；`import('./x.mjs')` 是异步动态导入。项目有模块顶层初始化，例如 `bootstrap.mjs` 直接创建应用；所以“导入”也可能触发配置读取、目录初始化和服务装配。不要把每个模块都理解成纯函数库。

`node:path`、`node:fs` 等类似 Python 标准库；相对路径是本仓库模块；`ws`、`express` 等来自 npm 依赖。`qwen-audio-agent/gateway-application` 是包公开导出路径，可能映射到一个内部 `.mjs` 文件，映射在根包的 `exports` 中。

## 3. 对象、解构与展开：读懂配置和依赖注入

实际接口见 [createGatewayApplication](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/gateway-application.mjs#L63)，下面是保留结构的简化片段：

```javascript
export function createGatewayApplication({
  config = defaultConfig,
  taskManager = null,
  autoStart = true,
} = {}) {
  // ...
}
```

这是一个参数对象，不是三个独立位置参数。调用方可以写 `createGatewayApplication({ taskManager: fakeManager })`，其他字段采用默认值；省略整个参数时使用 `{}`。

```python
def create_gateway_application(options=None):
    options = {} if options is None else options
    config = options.get("config", default_config)
    task_manager = options.get("taskManager", None)
    auto_start = options.get("autoStart", True)
```

注意：JavaScript 解构默认值针对缺失值或 `undefined`，传入 `null` 不会触发该默认值。Python 的 `.get()` 类比也需要注意键存在但值为空的情况。

```javascript
const { ownerId, sessionId = 'main', turnId } = context
const next = { ...context, ownerId, sessionId, turnId }
```

第一行从对象取字段；第二行创建浅拷贝，然后用后面的同名字段覆盖。简写 `ownerId` 等价于 `ownerId: ownerId`。数组的 `...items` 是展开；函数参数中的 `...args` 是收集剩余参数。**浅拷贝不会复制内层对象**，和 Python `dict.copy()` 类似。

证据：[TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57)、[createFrontendRuntime](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/app/frontend-runtime.mjs#L12)。读装配代码时，先把对象字段当成一张“依赖清单”。

## 4. 空值、布尔和常见集合操作

| JavaScript | 可借助的 Python 理解 | 必须注意 |
| --- | --- | --- |
| `const x = ...` | 定义局部名称 | 名称不能重新绑定，对象内部仍可修改 |
| `let x = ...` | 可重新赋值的变量 | 用于会变化的局部状态 |
| `value === other` | 类比 `==` | 不做宽松类型转换；对象比较主要看身份，不是结构内容 |
| `obj?.field` / `fn?.()` | 为空时跳过访问或调用 | 只针对 `null` / `undefined`；其他错误仍会抛出 |
| `x ?? fallback` | 只在空值时取默认 | 保留 `0`、`false`、空字符串 |
| `x \|\| fallback` | 类比 `x or fallback` | JS 的空数组、空对象为真，和 Python 不同 |
| `x \|\|= fallback` | 仅当 x 为假值才赋值 | 与解构默认值语义不同 |
| `array.map(f)` | `[f(x) for x in items]` | 通常返回新数组 |
| `array.filter(f)` | `[x for x in items if f(x)]` | 只保留满足条件的项 |
| `array.find(f)` | 找第一个匹配项 | 未找到返回 `undefined` |
| `Map` / `Set` | 类比 `dict` / `set` | `Map` 用 `.get/.set/.has`，`Set` 用 `.add/.has` |
| `` `backend:${ownerId}` `` | `f"backend:{owner_id}"` | 模板字符串可以插入表达式 |

真实例子：`this.requests = { permission: new Map(), input: new Map() }` 表示两个分别维护的请求表，不是两个后台队列。见 [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12)。

`Object.freeze(value)` 禁止直接修改被冻结对象的属性，但不会自动深度冻结所有嵌套内容。不要把它直接等同于 Python 的不可变深层数据结构。

## 5. 最关键差异：Promise 与 async/await

JavaScript 的 `async function` 被调用后，函数体会开始执行，直到需要暂停的 `await`，并立即向调用者返回 Promise。Python 调用 `async def` 通常只得到 coroutine，需要 `await` 或调度成 Task 才开始运行。

```javascript
async function run() {
  console.log('开始')
  await remoteCall()
  console.log('结束')
}
const pending = run() // 调用时已经开始
```

```python
async def run():
    print("开始")
    await remote_call()
    print("结束")

pending = asyncio.create_task(run())  # 安排给事件循环，随后开始
```

`await` 暂停的是当前异步函数，不是自动阻塞整个事件循环。但 `readFileSync`、同步子进程或大量 CPU 计算仍会阻塞所在线程。`async` 也不自动创建线程；项目显式使用 Worker 的地方另看。

本项目的核心例子是 [TaskManager.create / #create](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L428)：创建 Task 后通过 `queueMicrotask(() => this.drain())` 安排调度，并立即返回公开任务快照。后续执行结果由 Task 状态和事件管理。**这与调用者 `await backend.submit()` 等待完整工作结果不同。**

`queueMicrotask` 在当前执行栈结束后安排回调；用 `asyncio` 的调度概念可以帮助理解，但两种事件循环的队列和顺序不是一一对应。

### Promise 链怎么读

```javascript
operation()
  .then(value => handle(value))
  .catch(error => report(error))
  .finally(() => cleanup())
```

先类比 Python：

```python
try:
    value = await operation()
    handle(value)
except Exception as error:
    report(error)
finally:
    cleanup()
```

类比只帮助理解成功、失败、清理三个分支。链式回调的返回值会影响后续 Promise；抛出异常也会变成拒绝。项目中的 `.catch(() => {})` 有时只负责接住异步错误，不能据此判断业务成功。

`Promise.all([...])` 类比并发等待 `asyncio.gather(...)`；某项拒绝不自动取消其余操作。`Promise.resolve().then(fn)` 可以把调用放到微任务中；与普通同步调用不同。

## 6. 回调、闭包和事件：从“顺序脚本”转向“由事件驱动”

实际代码见 [TaskOperations.submit](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/task-operations.mjs#L57)：

```javascript
runner: (_objective, execution) => this.run({ objective, inputParts }, {
  ...execution, ownerId, sessionId, turnId,
})
```

`=>` 是箭头函数。这段代码把函数交给 TaskManager，后者在调度时调用；不是定义到这里就马上执行。函数保留外层的 `objective` 等值，这就是闭包。箭头函数保留外层 `this`，普通 JavaScript 函数的 `this` 会受调用方式影响。

Python 可以这样理解：

```python
async def runner(_objective, execution):
    return await self.run(
        {"objective": objective, "inputParts": input_parts},
        {**execution, "ownerId": owner_id, "sessionId": session_id},
    )
```

事件订阅是另一种回调：

```javascript
this.unsubscribe = this.taskManager.subscribe(event => this.handleEvent(event))
```

TaskManager 发布事实，订阅者处理通知、展示或持久化。`subscribe()` 返回取消订阅的函数，关闭时调用它防止旧连接继续接收事件。不要把事件发布默认理解成“另一个线程”或“消息队列中间件”；先看 `subscribe/emit` 实现。

在 [SessionTaskCoordinator](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/orchestration/session-task-coordinator.mjs#L12) 中同时找 `start`、`handleEvent` 和 `close`。这样比只读构造函数更容易看懂事件对象何时真正发挥作用。

## 7. 类、私有方法和取消

```javascript
export class TaskOperations {
  constructor({ taskManager, backendRuntime } = {}) {
    this.taskManager = taskManager
    this.backendRuntime = backendRuntime
  }
}
```

类比 Python 的 `class` 与 `__init__`。`new TaskOperations({...})` 创建实例；`this` 类比当前对象 `self`，但方法引用不能随意当成 Python 的绑定方法使用。`#create` 是语言级私有成员，只能在声明它的类内部访问。

项目用 `AbortController` / `AbortSignal` 传递取消信号。可以类比 Python 的协作式取消，但 `controller.abort()` 不保证外部进程已停止：操作必须响应 signal，后台 Adapter 也要执行对应取消协议。因此 Task 可能经过 `cancelling`，再到终态。见 [TaskManager.cancel](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-manager.mjs#L855)。

`setTimeout` / `setInterval` 类比定时调度；需要在关闭时清理。Node 的 `.unref()` 使该计时器不单独阻止进程退出，不代表它不再执行。

## 8. React 只先学够阅读的部分

`App.jsx` 描述界面组合，`useRealtimeVoice.js` 管理连接、音频与交互。后者虽叫 hook，仍包含普通 JavaScript 控制流。

- `useState`：会影响界面更新的状态。
- `useRef`：持有跨渲染的可变对象，修改它本身不触发重渲染。
- `useEffect`：在相关渲染之后执行副作用；返回函数用于清理连接、监听器等。
- JSX：界面描述，组件函数在渲染中使用，不等于服务端路由。

先沿 [useRealtimeVoice](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/web/src/realtime/useRealtimeVoice.js#L203)、[GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63)、[reduceGatewayClientState](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-state.mjs#L29) 理解数据如何进入界面，再看布局和 CSS。桌面主进程的 Electron API 与浏览器 React 是不同运行环境。

## 9. 实际读文件的五遍法

1. 看 import：它依赖哪个职责或协议？是否引入具体供应商？
2. 看 export / 构造参数：对外提供什么，依赖由谁注入？
3. 看状态：哪些 Map、Set、计时器或文件由它拥有？
4. 找入口方法：谁调用它？先看调用点，再读真正改变状态的分支。
5. 看 close / catch / finally / 测试：资源何时释放，失败如何呈现？

第一次遇到长对象或十几个依赖不必逐个背。先标出“输入、状态、动作、输出、清理”，就能借助 Python 经验阅读核心链路。
