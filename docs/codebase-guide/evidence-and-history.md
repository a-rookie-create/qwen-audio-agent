# 证据、版本与分析范围

[返回讲义入口](README.md) · [原文阅读地图](source-reading-map.md)

## 1. 本地基线

- 仓库：`QwenAudio/qwen-audio-agent`，本地 `main`。
- 源码分析日期：2026-10-03，Asia/Shanghai；按“原文阅读 + Python 解读”组织讲义的修订日期：2026-10-04。
- 源码分析基线：`f6dd0e3703d58e4941159c1be89447f3fcb5063a`，提交日期 2026-09-28。后续伴读文档提交不改变源码基线与行号。
- 根包版本：`2.0.1`；`v2.0.1` 指向 `a73bcbc`，源码基线是它后续的 `f6dd0e3`。
- 历史：非 shallow，共 810 条从源码基线可达的提交；不声称包含所有远端分支或开发前历史。
- 最早可达提交：`edb2365`，2026-07-26，137 文件、24849 行新增；已经是成形系统。
- 初次分析开始时没有本地未提交变更。伴读材料仅位于 `docs/codebase-guide/`，没有改动产品代码或原有手写文档；初版随后按用户要求提交至用户的 GitHub 仓库。

核对命令：`git rev-parse f6dd0e3`、`git rev-parse --is-shallow-repository`、`git log --reverse f6dd0e3`、`git show --stat edb2365`、`git tag --sort=version:refname`。历史路线日期使用 committer 时间；标签表展示被标记提交的时间，不等于 Release 页面发布时间或 tagger 时间。

## 2. 原文、讲义补充与验证的分工

**阅读主体：项目自带文档。** 产品目标、架构、使用说明、配置、协议和接口直接链接原文，由[原文地图](source-reading-map.md)按主题组织。八讲的必读表标明章节与问题，不另写一套配置或契约。

**讲义补充：阅读关系与 Python 桥梁。** 类比、教学代码、检查题和历史阶段划分帮助读原文，标为 teaching。它们不是项目新增接口，也不替代原文中的条件和例外。核心产品与架构从[README](../../README_ZH.md)、[架构总览](../architecture/overview.zh.md)进入；其余功能按课程或原文地图选读。

**验证依据：当前源码、配置和测试。** 原文机制的定位与必要补充分别链接到[代码索引](key-code-index.md)，准确路径、声明和行号存于 [code-landmarks.json](code-landmarks.json)。只在原文不足以解释当前分支时补源码说明，例如文字与打断的通知消费。遇到不同文档语境或版本差异，核对配置、装配和实现，不能把简化类比当作证明。

**外部概述仅作初次分析参考。** 曾参考用户提供的 [zread 页面](https://zread.ai/QwenAudio/qwen-audio-agent)，成功提取的是开篇概述，未取得完整目录所有章节；还缺失一处委派工具名称。讲义的原文阅读主线来自项目自身资料，不依赖该概述；本轮也未重新验证外部技术报告。

**历史与路线图：** 用来理解旧设计和演进动机，不直接证明当前行为。旧“协调 Agent”、已移除工具分类、旧数据目录和旧路径特别容易误导，应回到当前实现验证。

## 3. GitNexus 使用范围

MCP 最初返回无已索引仓库；CLI 首次尝试遇到全局注册目录写入限制。之后将 GitNexus 注册与索引都隔离到 `/tmp`，以 `--index-only --skip-fts` 建立分析索引，没有向仓库注入 AGENTS、技能或配置。

绑定仓库 `qwen-audio-agent`，索引提交 `f6dd0e3703d58e4941159c1be89447f3fcb5063a`，status 显示覆盖文件与基线一致。索引统计：1276 文件、23121 symbols、84232 edges、1266 processes。数字包含索引覆盖的测试等内容，不代表生产模块或实际运行流程数量。

使用精确符号 context 核对 TaskOperations、AgentTaskRuntime、SessionTaskCoordinator、createRealtimeSessionRuntime 等入口与关系。全文搜索未启用，概念 query 返回空不能证明没有路径；解析器还报告候选 / 流程截断。动态依赖注入、回调和协议分派通过源码与测试补证，图不是完整运行证明。

临时索引不是文档阅读的前置条件。后续若目录被清理，仍可直接用 `rg`、符号链接和 Git 历史复核。

## 4. 已验证与未验证

首次分析（2026-10-03）运行了 13 个现有测试文件，151 tests 全部通过；日志记录与命令归入[独立验证记录](operations/analysis-validation.md)。本轮讲义修订没有改产品代码，没有重跑完整产品测试；再次运行了 Python 教学模型。

本轮验收分别检查：八讲覆盖架构、启动、对话/工具、后台、记忆/知识、状态、客户端/扩展与运行；各讲提供原文阅读问题、Python 解读和检查题；原文地图链接全部 68 份项目中文文档（不含本讲义），并提供场景示例 README；链接及章节锚点、84 个源码定位和课程检查题/答案逐项核对。原项目文档与产品代码未改动。

本次没有实测云端实时模型、后台原生登录、真实麦克风 / 摄像头、WebRTC、手机、桌面成品或场景 benchmark。Mock 测试证明选择的内部分支，不证明外部模型必然遵守 Prompt，也不证明端到端延迟、可靠性或业务正确率。

Python 对照和练习脚本均为教学材料，不是 JavaScript 源码的等价实现。所有行为解释限定于当前代码基线；以后修改应刷新受影响章节和代码定位。

## 5. 本地可用发布标签

| 标签 | 提交 | 提交日期（Asia/Shanghai） |
| --- | --- | --- |
| `v0.9.0` | [9ca4356](https://github.com/QwenAudio/qwen-audio-agent/commit/9ca43561f007590870ae44cfd2279771e34d10b8) | 2026-07-28 19:47 |
| `v0.9.1` | [39faaf2](https://github.com/QwenAudio/qwen-audio-agent/commit/39faaf24cd1cea9e8e286cc12dd7208b702a6ede) | 2026-07-28 21:45 |
| `v0.10.0` | [5203e81](https://github.com/QwenAudio/qwen-audio-agent/commit/5203e81ec498271a6baf4a63b4b5de9f0fb88a9a) | 2026-07-30 00:16 |
| `v0.11.0` | [b5684ba](https://github.com/QwenAudio/qwen-audio-agent/commit/b5684ba1ead689559e515cfb7e96e12d55b64388) | 2026-07-30 04:56 |
| `v0.12.0` | [10e4014](https://github.com/QwenAudio/qwen-audio-agent/commit/10e4014df3b4886414a7170fa72317c842e9ffa3) | 2026-07-30 16:19 |
| `v0.12.1` | [ab203c2](https://github.com/QwenAudio/qwen-audio-agent/commit/ab203c2567334255c69606d88f334edac770ad5a) | 2026-07-30 18:10 |
| `v1.0.0` | [8249d1a](https://github.com/QwenAudio/qwen-audio-agent/commit/8249d1a682714576c14803649a8df74ba5240c39) | 2026-07-30 22:42 |
| `v1.1.0` | [cdc8c62](https://github.com/QwenAudio/qwen-audio-agent/commit/cdc8c62c4cb49d844c3f6ff61dc89d6526a08d7d) | 2026-07-31 11:32 |
| `v1.1.1` | [e069274](https://github.com/QwenAudio/qwen-audio-agent/commit/e0692748d26e30310ba135325aa6719c73d4cb95) | 2026-07-31 12:34 |
| `v1.2.0` | [b4aae10](https://github.com/QwenAudio/qwen-audio-agent/commit/b4aae10765f84b2c1cfceb91c1133484bd6b5524) | 2026-08-01 16:29 |
| `v1.3.0` | [03e3b2b](https://github.com/QwenAudio/qwen-audio-agent/commit/03e3b2bb8ba3035fc0746c5a004ab3456aff2b59) | 2026-08-03 22:27 |
| `v1.4.0` | [67dac77](https://github.com/QwenAudio/qwen-audio-agent/commit/67dac77367f2ba044dae3171b8d7ef569ecd51e9) | 2026-08-04 18:23 |
| `v1.4.1` | [f283252](https://github.com/QwenAudio/qwen-audio-agent/commit/f28325208002f41a7e7fc190a7ce0f7ded0f01f5) | 2026-08-04 21:29 |
| `v1.4.2` | [28fa940](https://github.com/QwenAudio/qwen-audio-agent/commit/28fa940d3b04b3692cec8601f095f8309a7da5d6) | 2026-08-05 12:04 |
| `v1.5.0` | [41c2f49](https://github.com/QwenAudio/qwen-audio-agent/commit/41c2f494fe87b45c8a237cd4212f8f3e559197ad) | 2026-08-05 23:36 |
| `v1.6.0` | [c66932a](https://github.com/QwenAudio/qwen-audio-agent/commit/c66932ab5f8a514f1d9b54e7c2b63662456813bd) | 2026-08-06 21:58 |
| `v1.6.1` | [491f4ba](https://github.com/QwenAudio/qwen-audio-agent/commit/491f4ba0ce1142faa417e3604013b3bc049cd89c) | 2026-08-07 14:09 |
| `v1.7.0` | [3aea601](https://github.com/QwenAudio/qwen-audio-agent/commit/3aea60140d3d0fd8bdaa65cf51b841db5d599544) | 2026-08-07 17:44 |
| `v1.8.0` | [a60cd1c](https://github.com/QwenAudio/qwen-audio-agent/commit/a60cd1c8f50bba1d5b4ec158ed12494affb49d20) | 2026-08-09 19:19 |
| `v1.8.1` | [27cac83](https://github.com/QwenAudio/qwen-audio-agent/commit/27cac835371c317164bbdc8378650c88e08bfa06) | 2026-08-11 00:48 |
| `v1.8.2` | [4bd2114](https://github.com/QwenAudio/qwen-audio-agent/commit/4bd2114ebdba60de7a74660064b07b56ff5f71fe) | 2026-08-11 23:00 |
| `v1.8.3` | [df7b913](https://github.com/QwenAudio/qwen-audio-agent/commit/df7b9133a0f947c988ee3b8379559047be04279a) | 2026-08-12 00:52 |
| `v1.9.0` | [7181551](https://github.com/QwenAudio/qwen-audio-agent/commit/71815519b54eeeff566037ed1d9020f6257ae651) | 2026-08-13 19:53 |
| `v1.9.1` | [9a829c4](https://github.com/QwenAudio/qwen-audio-agent/commit/9a829c464db47ebe853a8bc031ca4c32dfa13444) | 2026-08-13 20:31 |
| `v1.10.0` | [18b6588](https://github.com/QwenAudio/qwen-audio-agent/commit/18b6588e7b67536d48d16b50d43cceb44dc118fc) | 2026-08-13 22:42 |
| `v1.10.1` | [1dea877](https://github.com/QwenAudio/qwen-audio-agent/commit/1dea8779e73d9e1aaebfd8c6a847270cce39572f) | 2026-08-15 17:13 |
| `v1.11.0` | [c9fe9d0](https://github.com/QwenAudio/qwen-audio-agent/commit/c9fe9d02cd0f2d6b8dc54c75ad8e1d81b70549d2) | 2026-08-20 22:30 |
| `v2.0.0` | [3337d9b](https://github.com/QwenAudio/qwen-audio-agent/commit/3337d9b65c797d58e7acfacb9679b2976a2a4463) | 2026-09-23 18:01 |
| `v2.0.1` | [a73bcbc](https://github.com/QwenAudio/qwen-audio-agent/commit/a73bcbc2e1278bf664df38bdd169ffba1fb2451f) | 2026-09-26 21:40 |


CHANGELOG 包含 `0.2.0 / 0.5.0 / 0.6.0 / 0.7.0` 等更早版本说明，但本地没有同名标签。历史路线使用实际功能提交代替这些缺失标签，不创建或猜测发布 SHA。

## 6. 需要真实接入才能回答的问题

- 当前账号与模型组合下的语音延迟、额度、工具稳定性和图片 / 视频能力。
- 某个后台 Agent 的原生认证与配置是否在本机实际可用。
- 特定音频设备、操作系统和网络路径下的客户端行为。
- 场景业务策略与演示数据是否符合你的真实需求。

这些问题未被静态分析证明；查对应 Provider、后台与场景的配置并进行实际验证，才可形成结论。伴读解释的是框架已实现的边界与机制。
