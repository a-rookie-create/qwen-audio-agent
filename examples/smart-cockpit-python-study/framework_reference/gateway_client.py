"""客户端 SDK 做什么？对应 shared/gateway/client-sdk.mjs。
这是 SDK 的阅读模型；真正握手、认证、心跳、重连等合成伪操作。
"""


class GatewayClient:
    def start(self):
        连接Gateway并完成GCP握手()

    def send(self, event):
        按GCP协议编码并发送(event)

    def request(self, event_type, payload):
        return 发送请求并等待对应响应(event_type, payload)
