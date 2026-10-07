"""11 个车控工具的简化实现；真实状态更新仍统一交给 Store。"""
from __future__ import annotations
from service.tools.shared import ToolContext
from study_support import ToolResult

# 将用户参数中的区域名映射到实际状态字段，一次操作可以修改多个区域。
ZONES = {'driver': ['acTemp'], 'passenger': ['passengerTemp'], 'rear': ['rearTemp'],
         'front': ['acTemp', 'passengerTemp'], 'all': ['acTemp', 'passengerTemp', 'rearTemp']}
WINDOWS = {'windows': ['windowFL', 'windowFR', 'windowRL', 'windowRR'],
           'front': ['windowFL', 'windowFR'], 'rear': ['windowRL', 'windowRR'],
           'left': ['windowFL', 'windowRL'], 'right': ['windowFR', 'windowRR']}


async def execute(name: str, args: dict, ctx: ToolContext) -> ToolResult:
    before = ctx.snapshot()
    # 查询分支只读副本，直接返回结果，不增加版本或发布状态变化。
    if name == 'vehicle_location_query':
        return ctx.result('当前位置：演示车位', data={'location': before['location']})
    if name == 'vehicle_state_query':
        return ctx.result(f"当前主驾空调 {before['vehicle']['acTemp']} 度", data={'vehicle': before['vehicle']})
    vehicle = before['vehicle']
    action = args.get('action')
    changes: dict = {}
    # 控制分支先校验并计算 changes，直到函数末尾才统一提交，避免校验一半就修改状态。
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
        # set 使用绝对温度；increase/decrease 对每个区域的旧温度加减，并限制在支持范围。
        changes = {field: target if action == 'set' else min(32, max(16,
                   vehicle[field] + (delta if action == 'increase' else -delta))) for field in fields}
        changes['ac'] = True  # 调温同时打开空调，温度与开关在同一次更新中保存。
    elif name == 'vehicle_climate_control':
        # action 选择开关、预处理、模式或风量，对应到不同的状态字段。
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
        # 单窗或成组车窗先展开为字段名单，再统一写入 0–100 的开度。
        window = args.get('window', 'windows')
        keys = WINDOWS.get(window, [window])
        level = {'open': 100, 'close': 0, 'vent': 15}.get(action, args.get('level', 0))
        if not 0 <= level <= 100:
            raise ValueError('车窗开度需在 0–100 之间')
        # 嵌套 windows 字典要保留未选中的窗，再覆盖选中的窗，避免丢失其他窗口值。
        changes['windows'] = {**vehicle['windows'], **dict.fromkeys(keys, level)}
    elif name == 'vehicle_sunroof_control':
        # 将工具动作转换为状态值，例如 close -> closed、tilt -> vent。
        changes['sunroof'] = {'open': 'open', 'close': 'closed', 'vent': 'vent',
                              'tilt': 'vent', 'stop': 'stopped'}[action]
    elif name == 'vehicle_closure_control':
        # 只覆盖指定门/盖的开关，保留已有的其他目标记录。
        changes['closures'] = {**vehicle['closures'], args['target']: action == 'open'}
    elif name == 'vehicle_comfort_control':
        # 用“功能:座位”作为键，区分主驾/副驾等座位上的加热、通风等设置。
        key = args['target'] + ':' + args.get('seat', 'driver')
        value = args.get('level', 1) if action == 'set' else action == 'open'
        changes['comfort'] = {**vehicle['comfort'], key: value}
    elif name == 'vehicle_light_control':
        # 闪灯是一次动作：增加次数，但保持原来 headlights 的持续开关状态。
        changes['headlights'] = action == 'open' if action != 'flash' else vehicle['headlights']
        if action == 'flash':
            changes['flashLightsCount'] = vehicle.get('flashLightsCount', 0) + 1
    elif name == 'vehicle_sound_control':
        # 鸣笛累计动作次数；播放外放音效则保存选择的演示音效 ID。
        changes = {'hornCount': vehicle['hornCount'] + 1} if action == 'honk' else {'boomboxSound': args.get('soundId', 'demo')}
    elif name == 'vehicle_charging_control':
        # 充电操作分别修改开关、上限、电流或计划，涉及数值时先检查业务范围。
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
            # 列表推导式保留其他计划；添加时也构造新列表，不就地改旧计划列表。
            changes['chargeSchedules'] = [s for s in vehicle['chargeSchedules'] if s.get('id') != args.get('scheduleId')]
        else:
            changes['chargeSchedules'] = vehicle['chargeSchedules'] + [args.get('schedule', {})]
    else:
        raise ValueError('未知车控工具：' + name)
    # 所有校验通过后交给 Store：修改副本 -> 保存新版本 -> 通知 UI 和温度规则。
    state = ctx.update('vehicle', changes)
    return ctx.result('车辆操作已完成', ['vehicle'], {'vehicle': state['vehicle']})
