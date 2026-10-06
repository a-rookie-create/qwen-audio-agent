"""框架怎样联系后台？对应 BackendPort、A2A Adapter、BackendWorkRuntime。

BackendPort 是方法契约；协议细节由 Adapter 实现。
这里只展开 submit，其他方法用注释列出即可。
"""


class BackendPort:
    def submit(self, task):
        return 后台执行(task)
    # 完整契约还要求 describe/start/health/status/cancel、授权/补充输入、subscribe/close。


class A2ABackendAdapter:
    def __init__(self, agent_url):
        self.agent_url = agent_url

    def submit(self, task):
        # 读取 Agent Card、请求/流式事件、进度和结果转换，合成这一伪操作。
        return 经A2A联系后台并取得结果(self.agent_url, task)


def create_backend_agent_host(adapter):
    # 原框架校验 BackendPort，并加上宿主信息；不创建另一个后台模型。
    return adapter


class BackendWorkRuntime:
    def __init__(self, agent):
        self.agent = agent

    def run(self, task):
        return self.agent.submit(task)
