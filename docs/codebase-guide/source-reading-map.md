# 原文阅读地图

[讲义入口](README.md)

这里按学习问题归纳原项目资料。表中链接均指向原文；配置格式、能力限制、操作步骤和协议字段在原文中阅读。八讲指定了第一次应读的少量章节，本页用于按需展开。

## 1. 产品与架构：先建立全局

| 原文 | 读它解决什么问题 |
| --- | --- |
| [项目 README](../../README_ZH.md) | 产品目标、能力、原有架构图与应用场景 |
| [基本概念](../getting-started/concepts.zh.md) | 用户看到的前台、后台、会话和工作区是什么意思 |
| [架构总览](../architecture/overview.zh.md) | 逻辑组件、服务宿主、客户端与接口边界 |
| [详细架构](../architecture/deep-dive.zh.md) | 请求流、实时边界、后台 Session、状态、结果与依赖方向 |
| [服务端源码导航](../../server/src/README.md) | 原文中的职责如何映射到模块目录 |
| [架构演示文稿](../voice-agent-architecture-presentation.zh.md) | 用原有演示图串起对话、工作、委派、交付与记忆；区分通用架构与 ACP 示例 |
| [手册入口](../index.zh.md) | 原项目面向用户的操作阅读路线 |

## 2. 安装、配置与部署

| 原文 | 读它解决什么问题 |
| --- | --- |
| [安装与升级](../getting-started/install.zh.md) | 支持的运行环境、安装方式与升级 |
| [快速开始](../getting-started/quickstart.zh.md) | 完成第一次对话的操作步骤 |
| [配置总览](../configuration.zh.md) | 优先级、目录与不同设置的归属 |
| [语音前台设置](../configuration/frontend.zh.md) | 模型服务、凭据、音色与能力差异 |
| [后台通用设置](../configuration/backend.zh.md) | Agent、模型、工作区、权限和 Skills |
| [日志与诊断](../configuration/advanced.zh.md) | 日志位置、诊断与其他运行选项 |
| [Gateway 运行与常驻](../operations/gateway.zh.md) | 运行方式、实例、重启和进程所有权 |
| [远程连接与配对](../operations/remote-access.zh.md) | 连接码、设备、访问认证与远端检查 |
| [CLI 命令速查](../reference/cli.zh.md) | 查具体命令，避免凭记忆猜参数 |
| [故障排查](../operations/troubleshooting.zh.md) | 按连接、音频、后台、远程等边界定位问题 |

## 3. 对话、媒体与语音模型

| 原文 | 读它解决什么问题 |
| --- | --- |
| [对话与附件](../guides/conversation.zh.md) | 语音、文字、附件、静音与新会话的语义 |
| [视觉输入](../guides/vision.zh.md) | 文件附件、摄像头帧、按需采集为何不同 |
| [联网搜索](../guides/web-search.zh.md) | 搜索、网页读取与引用怎样参与前台回复 |
| [清单与提醒](../guides/notes-reminders.zh.md) | 条目数据、到点播报、定时执行的区别 |
| [Qwen Audio](../voice-frontends/qwen-audio-realtime.zh.md)、[Qwen Omni](../voice-frontends/qwen-omni-realtime.zh.md) | 项目内这些模型适配的配置与能力范围 |
| [GPT-Live](../voice-frontends/gpt-live.zh.md)、[Google Live](../voice-frontends/google-live.zh.md)、[StepAudio](../voice-frontends/stepfun.zh.md) | 相应服务的适配边界与验证范围 |
| [speech-to-speech](../voice-frontends/speech-to-speech.zh.md)、[MiniCPM-o](../voice-frontends/minicpm-o.zh.md) | 本地/自部署路径及与工具、视觉相关的限制 |
| [自定义 Realtime Provider](../voice-frontends/custom-provider.zh.md) | 供应商协议如何接到通用会话运行时，以及契约测试 |

## 4. 后台工作与 Agent 接入

| 原文 | 读它解决什么问题 |
| --- | --- |
| [后台工作与授权](../guides/tasks.zh.md) | 发起、补充、查询、取消和允许/拒绝 |
| [后台 Agent 总览](../backends/overview.zh.md) | 选一个现有后台及了解接入方式 |
| [各后台详细配置](../backends/configuration.zh.md) | 对应 Agent 的登录、启动来源与设置 |
| [接入新后台](../backends/extend.zh.md) | 通用 ACP、A2A、自定义 Adapter 与内置后台的不同路径 |
| [Backend Adapter SDK](../reference/backend-adapter-sdk.zh.md) | 通用方法、标准事件、结果、权限和输入的完整契约 |
| [A2A Backend Adapter](../reference/a2a-backend-adapter.zh.md) | 远端 Task、Context 与本地工作如何映射 |
| [后台 Skills](../guides/skills.zh.md) | Skill 安装位置、支持范围与生效方式 |

## 5. 个性化、记忆与知识

| 原文 | 读它解决什么问题 |
| --- | --- |
| [助手画像与偏好](../reference/personalization.zh.md) | 默认人设、明确长期要求与临时要求怎样区分 |
| [长期记忆](../reference/memory.zh.md) | 明确写入、自动整理、回溯与替换 Provider |
| [偏好学习机制](../reference/preference-learning.zh.md) | 观察推断的证据与晋升条件 |
| [Memory Provider](../reference/memory-provider.zh.md) | 上下文权威、控制面、同步快照与会话/音频观察 |
| [资料库指南](../guides/knowledge.zh.md) | 用户怎样开启、导入、查询和移除文档 |
| [知识库 Provider](../reference/knowledge.zh.md) | 检索与管理接口、本机基础实现、外部 RAG 接入 |

## 6. 客户端、协议与前台工具扩展

| 原文 | 读它解决什么问题 |
| --- | --- |
| [桌面版](../desktop/overview.zh.md)、[WebUI](../getting-started/webui.zh.md)、[TUI](../getting-started/tui.zh.md)、[移动端](../getting-started/mobile.zh.md) | 每种客户端的交互、设备与连接边界 |
| [Gateway 契约](../contract.zh.md) | 外部开发者可以依赖哪些公开入口 |
| [Gateway Client Protocol](../gateway-protocol.zh.md) | 握手、事件、命令、动作、回执、回放和信任边界 |
| [WebRTC 接入](../gateway-webrtc-client.zh.md) | 可选媒体传输的生命周期与部署边界 |
| [扩展总览](../extensions.zh.md) | 先选择正确扩展层，再看对应契约 |
| [前台 MCP](../reference/frontend-mcp.zh.md)、[前台 OpenAPI](../reference/frontend-openapi.zh.md) | 如何把明确启用的服务操作作为前台工具 |
| [Frontend Profile](../reference/frontend-profile.zh.md) | 人设与工具配置的组合方式及优先级 |
| [桌宠皮肤协议](../desktop/pet-skin-spec.zh.md)、[桌面动画对接](../reference/desktop-animations.zh.md) | 界面外观与运行状态如何衔接 |

## 7. 场景：看通用边界怎样支持不同业务

先看[原项目示例索引](../scenarios/index.zh.md)，再选一个与你的问题相关的示例。示例介绍用于进入，示例 README 提供完整配置、业务边界和验证条件。

| 场景原文 | 示例原文 | 重点观察 |
| --- | --- | --- |
| [智能座舱](../scenarios/smart-cockpit.zh.md) | [README](../../examples/smart-cockpit/README_ZH.md) | 客户端环境事件、前台工具与业务后台怎样组合 |
| [客服](../scenarios/customer-service.zh.md) | [README](../../examples/customer-service/README_ZH.md) | 业务状态、补充输入、批准与人工接管 |
| [X-Omni](../scenarios/x-omni.zh.md) | [README](../../examples/x-omni/README_ZH.md) | 视觉输入、按需采集与观察模式 |
| [AI Passport](../scenarios/ai-passport.zh.md) | [README](../../examples/ai-passport/README_ZH.md) | 外部硬件通过转发器接入客户端协议 |
| [LightRAG](../scenarios/lightrag.zh.md) | [README](../../examples/lightrag/README_ZH.md) | Node Provider 与外部知识服务的分工 |
| [VoiceMem](../scenarios/voicemem.zh.md) | [README](../../examples/voicemem/README_ZH.md) | Python Sidecar 与记忆生命周期 |
| [Memcode](../scenarios/memcode.zh.md) | [README](../../examples/memcode/README_ZH.md) | 托管记忆 API 的替换入口 |
| [数字人](../../examples/digital-human/README_ZH.md) | [设计原文](../../examples/digital-human/docs/design.zh.md) | 语音内容、播放时序与数字人客户端的结合 |
| [WebRTC](../gateway-webrtc-client.zh.md) | [README](../../examples/webrtc/README_ZH.md) | 更换客户端媒体传输，保留运行时语义 |

## 8. 演进、工程与验证资料

| 原文 | 用途与阅读时机 |
| --- | --- |
| [CHANGELOG](../../CHANGELOG.md) | 先看发布版本，再用[历史伴读](02-history-reading-route.md)选择功能提交 |
| [规划记录入口](../resources/planning.zh.md)、[前台能力规划](../frontend-agent-roadmap.md) | 了解当时为什么提出变更；历史记录与当前契约分开读 |
| [运行时 Roadmap](../roadmap/frontend-chatbot-runtime.zh.md)、[协议 Roadmap](../roadmap/gateway-client-protocol.zh.md)、[远程接入 Roadmap](../roadmap/gateway-remote-access.zh.md) | 已有整体架构后，追演进阶段与设计约束 |
| [技术资料](../resources/presentations.zh.md)、[论文索引](../resources/papers.zh.md) | 找项目提供的演示文稿与外部报告入口；本讲义未重新验证外部报告 |
| [前台 Runtime 评测](../reference/frontend-evaluations.zh.md) | 区分确定性运行时验证与模型语义质量评测 |
| [贡献指南](../../CONTRIBUTING.md)、[CI 配置](../../.github/workflows/ci.yml)、[根包脚本](../../package.json) | 理解测试、构建、发布与工程检查 |
| [隐私说明](../../PRIVACY.md)、[安全说明](../../SECURITY.md) | 核对数据流向与项目安全问题的处理入口 |

英文对应文档可从原项目[英文手册入口](../index.md)查找。宣传稿与历史推广文案不作为当前能力依据。
