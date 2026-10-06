"""客户端怎样获得业务状态？对应 useCockpitState.js。
HTTP/SSE 直接连接座舱 Service，与语音 GCP 连接分开。
"""


class CockpitStateController:
    def load(self):
        return HTTP_GET('/api/cockpit/state')

    def subscribe(self, on_state):
        SSE订阅('/api/cockpit/events', on_state)

    def execute(self, name, arguments):
        return HTTP_POST('/api/cockpit/commands', {'name': name, 'arguments': arguments})
        # 点击车辆面板可直接执行命令，不必先让模型推理。
