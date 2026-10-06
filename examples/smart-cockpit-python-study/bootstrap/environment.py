"""环境加载只解决配置来源，对应 bootstrap/environment.mjs。
优先级：进程已有变量 > 座舱 .env.local > 仓库 .env.local。
"""


def load_cockpit_environment(env):
    合并缺失配置(env, 座舱环境文件)
    合并缺失配置(env, 仓库环境文件)
    return env
