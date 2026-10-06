"""天气工具：外部查询 → 保存状态 → 返回结果，对应 executeWeatherTool。"""


def execute(name, arguments, state):
    weather = 查询天气(arguments.get('city', '杭州'))
    if not weather:
        return '天气查询失败'            # 未取得数据，不把查询说成成功。
    return state.update('weather', weather)
