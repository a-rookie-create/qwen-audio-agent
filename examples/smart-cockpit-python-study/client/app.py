"""客户端做什么？对应原 App.jsx，React 组件改写成简单教学类。

客户端负责输入和展示；业务执行交给 Service，语音交互交给 Gateway。
"""


class CockpitApp:
    def __init__(self):
        self.voice = VoiceSessionController()   # 连接 Gateway。
        self.cockpit = CockpitStateController() # 连接业务 Service。

    def on_user_speaks(self, audio):
        self.voice.send_audio(audio)

    def on_user_clicks_panel(self, tool_name, arguments):
        self.cockpit.execute(tool_name, arguments)

    def on_gateway_reply(self, reply):
        展示对话并播放音频(reply)

    def on_service_state(self, state):
        更新车辆地图音乐等面板(state)
        # 记忆、技能、人设面板各有接入入口，按需再读对应模块。
