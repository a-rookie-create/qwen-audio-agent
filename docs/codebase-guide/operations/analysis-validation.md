# 讲义分析与验证记录

[讲义入口](../README.md) · [运行与验证讲义](runtime-and-tests.md)

这里记录讲义作者实际做过的验证，与供读者选读的测试入口分开。2026-10-04 本轮修改只涉及讲义组织和链接，未改产品代码，也未重新运行完整产品测试。

## 首次分析已执行的测试

首次分析日期 2026-10-03，代码 `f6dd0e3`。分三组直接运行 Node 内置测试，共 **151 tests，151 pass，0 fail**，涉及 13 个文件：

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


## 本轮讲义检查

核对原文链接及章节锚点、引用的源码文件与基线行号、课程顺序、各讲检查题与答案的对应关系。再次执行 Python 教学模型，仅用于确认教学示例仍可运行。原文和产品代码保持原样。最终检查结果见[证据记录](../evidence-and-history.md)。
