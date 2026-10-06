"""外部业务能力怎样隔离？教学接口，对应高德与车辆定位适配。
工具依赖这些能力，不直接关心供应商请求格式。
"""


class ScenarioServices:
    def weather(self, city):
        return 调用天气服务(city)

    def plan_route(self, origin, destination, waypoints):
        return 调用地图路线规划(origin, destination, waypoints)

    def vehicle_location(self):
        return 读取车机定位或标记来源的Demo回退()
