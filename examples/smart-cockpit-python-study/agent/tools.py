"""后台工具怎样组合？对应 agent/tools.mjs。
业务工具走 MCP，网页工具复用框架的检索能力。
"""


class CockpitAgentTools:
    def __init__(self, cockpit, retrieval):
        self.cockpit, self.retrieval = cockpit, retrieval

    def list(self):
        return self.cockpit.list() + 配置中可用的网页工具目录()

    def call(self, name, arguments):
        if name == 'web_search':
            return self.retrieval.search(arguments['query'])
        if name == 'fetch_url':
            return self.retrieval.fetch_url(arguments['url'])
        return self.cockpit.call(name, arguments)
        # 检索失败应返回失败事实；不能编造已经核验的来源。
