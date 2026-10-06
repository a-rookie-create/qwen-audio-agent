"""根据实际领域路由描述委派边界；不执行任务。"""


def create_cockpit_spawn_thinking_description(routing: dict[str, str]) -> str:
    frontend = [domain for domain, side in routing.items() if side == 'frontend']
    backend = [domain for domain, side in routing.items() if side == 'backend']
    return f'前台领域：{frontend}；后台领域：{backend}。混合意图按工具归属拆分，研究可交给后台。'
