"""11 个车控工具的简化实现；真实状态更新仍统一交给 Store。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult

ZONES = {'driver': ['acTemp'], 'passenger': ['passengerTemp'], 'rear': ['rearTemp'],
         'front': ['acTemp', 'passengerTemp'], 'all': ['acTemp', 'passengerTemp', 'rearTemp']}
WINDOWS = {'windows': ['windowFL', 'windowFR', 'windowRL', 'windowRR'],
           'front': ['windowFL', 'windowFR'], 'rear': ['windowRL', 'windowRR'],
           'left': ['windowFL', 'windowRL'], 'right': ['windowFR', 'windowRR']}


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    before = ctx.snapshot()
    if name == 'vehicle_location_query':
        return ctx.result('当前位置：演示车位', data={'location': before['location']})
    if name == 'vehicle_state_query':
        return ctx.result(f"当前主驾空调 {before['vehicle']['acTemp']} 度", data={'vehicle': before['vehicle']})
    vehicle = before['vehicle']
    action = args.get('action')
    changes: dict = {}
    if name == 'vehicle_temperature_control':
        if action == 'set' and 'temperature' not in args:
            raise ValueError('设置温度需要 temperature 参数')
        fields = ZONES[args.get('zone', 'all')]
        delta = args.get('delta', 1)
        if not 0.5 <= delta <= 10:
            raise ValueError('调整幅度需在 0.5–10 度之间')
        target = args.get('temperature', 22)
        if action == 'set' and not 16 <= target <= 32:
            raise ValueError('温度需在 16–32 度之间')
        changes = {field: target if action == 'set' else min(32, max(16,
                   vehicle[field] + (delta if action == 'increase' else -delta))) for field in fields}
        changes['ac'] = True
    elif name == 'vehicle_climate_control':
        if action in {'open', 'close'}:
            changes['ac'] = action == 'open'
        elif action in {'start', 'stop'}:
            changes['preconditioning'] = action == 'start'
        elif action == 'set_mode':
            changes['acMode'] = args['mode']
        else:
            if not 1 <= args.get('fan', 0) <= 8:
                raise ValueError('风量需在 1–8 档之间')
            changes['acFan'] = args['fan']
    elif name == 'vehicle_window_control':
        window = args.get('window', 'windows')
        keys = WINDOWS.get(window, [window])
        level = {'open': 100, 'close': 0, 'vent': 15}.get(action, args.get('level', 0))
        if not 0 <= level <= 100:
            raise ValueError('车窗开度需在 0–100 之间')
        changes['windows'] = {**vehicle['windows'], **dict.fromkeys(keys, level)}
    elif name == 'vehicle_sunroof_control':
        changes['sunroof'] = {'open': 'open', 'close': 'closed', 'vent': 'vent',
                              'tilt': 'vent', 'stop': 'stopped'}[action]
    elif name == 'vehicle_closure_control':
        changes['closures'] = {**vehicle['closures'], args['target']: action == 'open'}
    elif name == 'vehicle_comfort_control':
        key = args['target'] + ':' + args.get('seat', 'driver')
        value = args.get('level', 1) if action == 'set' else action == 'open'
        changes['comfort'] = {**vehicle['comfort'], key: value}
    elif name == 'vehicle_light_control':
        changes['headlights'] = action == 'open' if action != 'flash' else vehicle['headlights']
        if action == 'flash':
            changes['flashLightsCount'] = vehicle.get('flashLightsCount', 0) + 1
    elif name == 'vehicle_sound_control':
        changes = {'hornCount': vehicle['hornCount'] + 1} if action == 'honk' else {'boomboxSound': args.get('soundId', 'demo')}
    elif name == 'vehicle_charging_control':
        if action in {'start', 'stop'}:
            changes['charging'] = action == 'start'
        elif action == 'set_limit':
            if not 0 <= args.get('limitPercent', -1) <= 100:
                raise ValueError('充电上限需在 0–100 之间')
            changes['chargeLimit'] = args['limitPercent']
        elif action == 'set_amps':
            if args.get('amps', 0) <= 0:
                raise ValueError('充电电流必须为正数')
            changes['chargingAmps'] = args['amps']
        elif action in {'standard', 'max_range'}:
            changes['chargeMode'] = action
        elif action == 'remove_schedule':
            changes['chargeSchedules'] = [s for s in vehicle['chargeSchedules'] if s.get('id') != args.get('scheduleId')]
        else:
            changes['chargeSchedules'] = vehicle['chargeSchedules'] + [args.get('schedule', {})]
    else:
        raise ValueError('未知车控工具：' + name)
    state = ctx.update('vehicle', changes)
    return ctx.result('车辆操作已完成', ['vehicle'], {'vehicle': state['vehicle']})
