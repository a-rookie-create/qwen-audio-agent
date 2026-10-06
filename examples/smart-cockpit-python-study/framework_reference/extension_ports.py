"""扩展接口是什么？对应 memory/provider、knowledge/provider 等契约。
方法表达职责即可；不学习 Protocol 类型声明或完整参数校验。
"""


class MemoryProvider:
    def list(self, user):
        return 读取该用户的记忆快照(user)  # 原接口要求同步快照读取。

    def apply(self, user, changes):
        保存记忆修改(user, changes)


class KnowledgeProvider:
    def retrieve(self, question):
        return 从知识库检索(question)


class WebRetrieval:
    def search(self, query):
        return 搜索公开网页(query)

    def fetch_url(self, url):
        return 读取公开网页正文(url)


# 这里只列核心用途；各接口还需身份/能力描述。
# Realtime Provider 负责实时模型连接、认证和供应商事件转换，原版用注册对象表示。
