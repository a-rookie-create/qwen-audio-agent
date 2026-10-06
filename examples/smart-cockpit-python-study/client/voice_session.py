"""客户端怎样接入语音？对应 useVoiceSession.js。
收音/播放属于客户端；模型调用由 Gateway 当前会话接入。
"""


class VoiceSessionController:
    def __init__(self):
        self.gateway = GatewayClient()

    def send_audio(self, audio):
        self.gateway.send({'type': 'audio.append', 'audio': 音频编码(audio)})

    def on_audio_reply(self, audio, response_id):
        播放音频(audio)
        播放结束后发送回执(self.gateway, response_id)
        # 收到音频不等于播完；真实播放回执帮助框架确认结果送达。

    def publish_event(self, name, data):
        return self.gateway.request('client.event.publish', {'name': name, 'data': data})
