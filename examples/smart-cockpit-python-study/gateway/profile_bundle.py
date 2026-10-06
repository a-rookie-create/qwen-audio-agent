"""前台配置怎样准备？对应 gateway/profile-bundle.mjs。
原入口根据工具路由生成 Profile 与 MCP 配置，使实际目录与提示一致。
"""


def create_cockpit_frontend_mcp_configuration(url, frontend_tools):
    return {'工具服务地址': url, '允许的前台工具': frontend_tools}


def write_cockpit_frontend_profile_bundle(config):
    保存人设Markdown(config)
    保存前台MCP配置(config)
    return 保存Profile并返回路径(config)
    # Gateway 启动后读取这些配置；这一步不执行工具，也不调用模型。
