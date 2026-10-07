"""12 个导航工具共用离线路线适配；多途经点仍可由前台执行。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    state = ctx.snapshot()
    nav = state['navigation']
    changes: dict = {}
    # 先区分无需路线计算的操作；停止导航会清空当前路线，但保留收藏和显示设置。
    if name == 'navigation_stop':
        changes = {'status': 'idle', 'destination': None, 'waypoints': [], 'route': None}
    elif name == 'navigation_search_place':
        # 地点搜索只返回候选列表，不选择目的地或启动导航。
        return ctx.result('地点搜索完成（离线演示）', data={'places': ctx.services.search_places(args.get('query', ''))})
    elif name == 'navigation_set_favorite':
        # 参数决定用当前位置还是指定地址；新建收藏字典并保留其他收藏。
        address = state['location']['address'] if args.get('useCurrentLocation') else args.get('address')
        if not address:
            raise ValueError('收藏需要地址')
        changes = {'favorites': {**nav['favorites'], args['favoriteType']: address}}
    elif name == 'navigation_set_voice':
        # 未提供的设置沿用旧值，避免只改静音时连播报模式也被覆盖。
        changes = {'muted': args.get('mute', nav['muted']),
                   'broadcastMode': args.get('broadcastMode', nav['broadcastMode'])}
    elif name == 'navigation_set_view':
        changes = {'viewMode': args['viewMode']}
    else:
        # 涉及路线的操作共用下面的规划逻辑，缺省参数沿用当前目的地与途经点。
        destination = args.get('destination', nav['destination'])
        waypoints = list(args.get('waypoints', nav['waypoints']))  # 复制后再插入/删除，保护旧列表。
        if name == 'navigation_to_favorite':
            destination = nav['favorites'].get(args['favoriteType'])
        elif name == 'navigation_add_waypoint':
            # next 插到首位作为下一站，其他情况追加到最后。
            waypoints.insert(0 if args.get('insertPosition') == 'next' else len(waypoints), args['waypoint'])
        elif name == 'navigation_remove_waypoint':
            # 支持按索引或名称删除；不存在时抛错，尚未提交任何状态。
            if 'index' in args:
                waypoints.pop(args['index'])
            elif args.get('waypoint') in waypoints:
                waypoints.remove(args['waypoint'])
            else:
                raise ValueError('找不到途经点')
        if not destination:
            # 改途经点/偏好也需要已有最终目的地，才能重新计算完整路线。
            raise ValueError('请先指定最终目的地')
        strategy = args.get('strategy', nav['strategy'])
        # 外部适配器统一计算路线；本学习版只返回带演示来源的固定计算结果。
        route = ctx.services.plan_route(state['location']['address'], destination, waypoints, strategy)
        # 查询路线保存预览，显式开始才进入 navigating；其他修改沿用当前导航状态。
        status = 'preview' if name == 'navigation_route_query' else 'navigating' if name in {
            'navigation_start', 'navigation_to_favorite'} else nav['status']
        changes = {'destination': destination, 'waypoints': waypoints, 'strategy': strategy,
                   'route': route, 'status': status}
    # 统一提交 navigation 领域；客户端同步后还会将新导航事实送到前台模型上下文。
    after = ctx.update('navigation', changes)
    route = after['navigation']['route']
    text = f"路线 {route['distanceKm']} 公里，约 {route['minutes']} 分钟（演示）" if route else '导航状态已更新'
    return ctx.result(text, ['navigation'], {'navigation': after['navigation']})
