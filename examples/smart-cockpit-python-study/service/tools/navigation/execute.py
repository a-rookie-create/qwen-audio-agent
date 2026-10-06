"""导航工具怎样工作？对应 executeNavigationTool。
多途经点也可由前台工具执行，不需要自动委派后台。
"""


def execute(name, arguments, state):
    if name == 'navigation_stop':
        return state.update('navigation', 清空当前路线())
    if name in {'navigation_start', 'navigation_route_query'}:
        locations = 解析目的地和途经点(arguments)
        route = 调用地图规划(locations)
        return state.update('navigation', 生成路线状态(name, route))
    return 执行其它导航分支(name, arguments, state)
    # 原版另有途经点编辑、收藏、偏好等，本页不展开。
