"""根据实际领域路由描述委派边界；不执行任务。"""


def create_cockpit_spawn_thinking_description(routing: dict[str, str]) -> str:
    # 从实际路由表归纳前后台领域，生成可读说明；这里只生成字符串，不提交任务。
    frontend = [domain for domain, side in routing.items() if side == 'frontend']
    backend = [domain for domain, side in routing.items() if side == 'backend']
    return f'前台领域：{frontend}；后台领域：{backend}。混合意图按工具归属拆分，研究可交给后台。'
