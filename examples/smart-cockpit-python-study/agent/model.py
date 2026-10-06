"""后台怎样调用模型？对应 agent/model.mjs。
原版用 OpenAI 风格客户端调用 DashScope；这是参数思想，不涉及安装 SDK。
"""


class DashScopeCockpitModel:
    def __init__(self, client):
        self.client = client

    def complete(self, messages, tools):
        # 把对话历史和工具目录交给模型，取得文字或工具调用。
        response = self.client.chat.completions.create(
            model='qwen3.8-flash', messages=messages, tools=tools,
        )
        return response.choices[0].message
