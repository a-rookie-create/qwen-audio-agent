"""座舱怎样使用框架？对应原 gateway/server.mjs。

只保留组装思想；参数是教学归纳。真实 JS 入口还加载环境与 Profile。
"""


def start_cockpit_gateway():
    # 1. 后台接入对象知道如何经 A2A 联系独立的座舱 Agent。
    adapter = A2ABackendAdapter(后台Agent地址)
    agent_host = create_backend_agent_host(adapter)

    # 2. 场景提供人设、前台工具配置和环境事件；框架负责装配。
    application = create_gateway_application(
        agent=agent_host,
        config=座舱配置,  # 包含实时模型、人设、前台 MCP 与场景事件配置。
    )

    # 3. 开始监听，客户端才能连接。
    application.start()
    return application


# 原文件先等待 Service /health 就绪，再启动；等待细节本页省略。
