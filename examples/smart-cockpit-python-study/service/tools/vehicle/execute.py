"""车控的核心：查询或修改权威状态，对应 executeVehicleTool。
只展开温度设置路径；完整温区、参数校验等交给一个伪操作。
"""


def execute(name, arguments, state):
    if name == 'vehicle_state_query':
        return state.snapshot()['vehicle']
    if name == 'vehicle_temperature_control':
        changes = 根据温区和参数计算温度修改(arguments)
        # 默认温区 all；设置范围 16–32，相对调整限幅，并打开空调。
        return state.update('vehicle', changes)
    return 执行对应车控操作(name, arguments, state)
