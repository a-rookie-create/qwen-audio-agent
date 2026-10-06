"""12 个导航工具共用离线路线适配；多途经点仍可由前台执行。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    state = ctx.snapshot()
    nav = state['navigation']
    changes: dict = {}
    if name == 'navigation_stop':
        changes = {'status': 'idle', 'destination': None, 'waypoints': [], 'route': None}
    elif name == 'navigation_search_place':
        return ctx.result('地点搜索完成（离线演示）', data={'places': ctx.services.search_places(args.get('query', ''))})
    elif name == 'navigation_set_favorite':
        address = state['location']['address'] if args.get('useCurrentLocation') else args.get('address')
        if not address:
            raise ValueError('收藏需要地址')
        changes = {'favorites': {**nav['favorites'], args['favoriteType']: address}}
    elif name == 'navigation_set_voice':
        changes = {'muted': args.get('mute', nav['muted']),
                   'broadcastMode': args.get('broadcastMode', nav['broadcastMode'])}
    elif name == 'navigation_set_view':
        changes = {'viewMode': args['viewMode']}
    else:
        destination = args.get('destination', nav['destination'])
        waypoints = list(args.get('waypoints', nav['waypoints']))
        if name == 'navigation_to_favorite':
            destination = nav['favorites'].get(args['favoriteType'])
        elif name == 'navigation_add_waypoint':
            waypoints.insert(0 if args.get('insertPosition') == 'next' else len(waypoints), args['waypoint'])
        elif name == 'navigation_remove_waypoint':
            if 'index' in args:
                waypoints.pop(args['index'])
            elif args.get('waypoint') in waypoints:
                waypoints.remove(args['waypoint'])
            else:
                raise ValueError('找不到途经点')
        if not destination:
            raise ValueError('请先指定最终目的地')
        strategy = args.get('strategy', nav['strategy'])
        route = ctx.services.plan_route(state['location']['address'], destination, waypoints, strategy)
        status = 'preview' if name == 'navigation_route_query' else 'navigating' if name in {
            'navigation_start', 'navigation_to_favorite'} else nav['status']
        changes = {'destination': destination, 'waypoints': waypoints, 'strategy': strategy,
                   'route': route, 'status': status}
    after = ctx.update('navigation', changes)
    route = after['navigation']['route']
    text = f"路线 {route['distanceKm']} 公里，约 {route['minutes']} 分钟（演示）" if route else '导航状态已更新'
    return ctx.result(text, ['navigation'], {'navigation': after['navigation']})
