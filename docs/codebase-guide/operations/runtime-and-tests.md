# 运行与测试：先验证理解，再接入真实服务

[返回伴读入口](../README.md) · 实践：[练习与答案](../exercises/reading-workbook.md)

## 1. 阅读不要求启动所有能力

第一遍使用 `git show`、编辑器搜索和现有测试即可。理解正常链路之后，先运行当前版本的普通对话，再接后台；随后增加一个前台工具或一个示例。每次只增加一项外部依赖，便于判断错误属于哪层。

下面命令是供你按需操作的阅读材料，本次没有安装 npm 依赖、登录后台、修改日常配置或启动真实云端对话。

## 2. 当前基线的源码运行入口

安装要求以[仓库安装文档](../../getting-started/install.zh.md)、[package.json](../../../package.json)、[.nvmrc](../../../.nvmrc)为准。本次基线的 `.nvmrc` / `.node-version` 固定到 `22.22.2`；安装文档列出 `^22.22.2`、`^24.15.0` 或 `>=26.0.0` 与 npm 10+。

```bash
# 在仓库根目录，已使用适配的 Node.js 环境
npm ci
npm run build
npm run cli -- config

# 按生成配置填入前台模型信息后启动
npm run gateway

# 另一终端连接 WebUI
npm run cli -- webui
```

`npm run dev` 启动开发 server / web；`npm run desktop` 启动 Electron 开发入口；`npm run cli -- ...` 和 `npm run gateway` 从本仓库启动。全局安装的 `qwenaudio` 可能来自另一版本，调试时要确认你运行哪份代码。

配置命令会创建缺失模板；Gateway 导入配置也可能初始化目录。若要独立学习配置，可以先设置 `QWAUDIO_CONFIG_DIR` 到专用目录。模型 API Key、后台自身登录与 Gateway 客户端接入凭据有不同用途；沿对应模块查找，不要把它们混为一个“配置成功”。

## 3. 每层如何判断成功

| 检查点 | 能证明什么 | 不能单独证明什么 |
| --- | --- | --- |
| 版本 / 配置路径 | 当前程序版本和使用的配置位置 | 模型或后台连通 |
| Gateway 监听 / health | 服务和返回的健康信息 | 实际麦克风输入、所有模型能力可用 |
| GCP session.ready | 客户端协议握手成功 | Realtime 认证、后台登录成功 |
| 前台模型 ready / connected | 当前 Provider 会话状态 | 每个工具和后台业务操作成功 |
| accepted Task 回执 | 本地工作受理 | 外部操作完成 |
| completed Task | 执行返回完成结果 | 客户端已开始播放 |
| playback.started | 对应音频已开始交付 | 用户听完或业务结果正确 |

依据：[Gateway process entry](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/index.mjs#L1)、[GatewayClient](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/shared/gateway/client-sdk.mjs#L63)、[attachGatewayClientTransport](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/transport/gateway-client-transport.mjs#L62)、[AgentTaskRuntime.executeSpawnThinkingToolCall](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/frontend/tools/agent-task-runtime.mjs#L195)、[TaskStatus / TRANSITIONS](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/task/task-state.mjs#L5)、[AnnouncementManager](https://github.com/QwenAudio/qwen-audio-agent/blob/f6dd0e3703d58e4941159c1be89447f3fcb5063a/server/src/voice/announcement/announcement-manager.mjs#L66)。

## 4. 本次运行了哪些现有测试

分析日期 2026-10-03，代码 `f6dd0e3`。分三组直接运行 Node 内置测试，共 **151 tests，151 pass，0 fail**，涉及 13 个文件：

| 文件 | 对伴读解释提供的验证 |
| --- | --- |
| `server/test/task-state.test.mjs` | 内部状态 / 公开工作状态、合法转换 |
| `server/test/task-manager.test.mjs` | 即时受理、串行入口、delegated 让出通道、取消、通知、去重 |
| `server/test/backend-work-runtime.test.mjs` | 统一 BackendPort 输入、隔离工作、取消与状态接口 |
| `server/test/session-task-coordinator.test.mjs` | 权限 / 输入投递、重连、关闭释放 claim、工作继续 |
| `server/test/task-notification-queue.test.mjs` | 领取、续期、释放、过期与交付 |
| `server/test/dependency-boundaries.test.mjs` | 模块依赖方向、接入与业务职责边界 |
| `server/test/announcement-window.test.mjs` | 说话 / 回复 / 播放窗口 |
| `server/test/task-store.test.mjs` | 工作持久化、损坏处理、延迟写与终态写 |
| `server/test/session-journal.test.mjs` | 日志追加、读取、恢复和规范化 |
| `server/test/permission-policy.test.mjs` | 任务 / 会话范围的权限策略 |
| `server/test/announcement-manager.test.mjs` | 生成与播放确认分离、批次、有界重试 |
| `server/test/task-repository.test.mjs` | 仓储状态与持久化行为 |
| `server/test/realtime-presentation-runtime.test.mjs` | 音频展示、播放生命周期、主动打断确认与迟到输出 |

测试运行环境为宿主 Node `v25.9.0`，它不在仓库声明的支持版本范围内；本次通过结果应连同该限制理解。日常运行和复现建议使用仓库指定版本，不把这里的通过视为新增 Node 25 支持。

首次运行有一个测试因配置初始化尝试写默认用户目录而失败；随后把配置、数据、状态、缓存全部指向 `/tmp` 的学习专用目录，同一组用例通过。此处报告的是隔离后完整通过结果。

在仓库根目录复现：

```bash
QWAUDIO_CONFIG_DIR=/tmp/qwen-audio-agent-guide-test-config \
QWAUDIO_DATA_DIR=/tmp/qwen-audio-agent-guide-test-data \
QWAUDIO_STATE_DIR=/tmp/qwen-audio-agent-guide-test-state \
QWAUDIO_CACHE_DIR=/tmp/qwen-audio-agent-guide-test-cache \
node --test \
  server/test/task-state.test.mjs \
  server/test/task-manager.test.mjs \
  server/test/backend-work-runtime.test.mjs \
  server/test/session-task-coordinator.test.mjs \
  server/test/task-notification-queue.test.mjs \
  server/test/dependency-boundaries.test.mjs \
  server/test/announcement-window.test.mjs \
  server/test/task-store.test.mjs \
  server/test/session-journal.test.mjs \
  server/test/permission-policy.test.mjs \
  server/test/announcement-manager.test.mjs \
  server/test/task-repository.test.mjs \
  server/test/realtime-presentation-runtime.test.mjs
```

这个命令只跑已选用例，没有执行 npm 全套测试中的示例依赖安装前置脚本。所选测试使用伪边界或临时资源，不进行真实云端语音对话。

## 5. 继续验证时按问题选择测试

- 想理解模型 / 工具生命周期：`realtime-session-runtime.test.mjs`、`tool-call-handler.test.mjs`。
- 想理解统一用户操作：`task-operations.test.mjs`、`client-command-runtime.test.mjs`。
- 想理解不同 Provider：`realtime-provider-behavior.test.mjs` 和具体 Provider 用例。
- 想理解协议：`gateway-client-handshake.test.mjs`、`gateway-client-protocol-session.test.mjs`。
- 想理解裁剪：`optional-modules-pruning.test.mjs`，它会在临时副本中处理领域目录。

这些是代码里已存在的继续阅读入口，**本次未运行**。需要真实云模型、后台进程、浏览器音频或 WebRTC 的场景，应按各自配置再验证；Mock 通过不能替代实际接入验证。

## 6. 读日志的顺序

先用关联 ID 确认 owner / session / turn / response / call / Task，再判断问题发生在客户端连接、模型、工具、后台执行还是通知播放。关键日志和状态在各自职责模块，而不是只有一个文件能解释全部错误。

不要仅因界面显示“正在处理”就认定后台仍在运行。先查询 Task，再核对最新活动和当前待授权 / 待输入；若 Task 已完成，再沿 notification / playback 链检查。
