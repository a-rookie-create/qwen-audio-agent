"""可运行的记忆/知识/网页能力；默认数据在内存，网页内容是离线夹具。"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4


class MemoryConflictError(ValueError):
    pass


class MemoryProvider:
    def __init__(self) -> None:
        self.documents: dict[str, list[dict]] = {}
        # 按用户保存记忆，读取总是返回副本，外部无法直接修改 Provider 的记录。

    def list(self, owner_id: str) -> list[dict]:
        return deepcopy(self.documents.get(owner_id, []))

    def apply(self, owner_id: str, changes: list[dict]) -> list[dict]:
        # 整批变更先作用于副本；任何一步校验失败，都不会保存前面已处理的部分。
        documents = self.list(owner_id)
        for change in changes:
            if change['operation'] == 'add':
                documents.append({'id': uuid4().hex, 'text': change['text'], 'version': 1})
            elif change['operation'] == 'remove':
                current = next((d for d in documents if d['id'] == change['id']), None)
                # 用读取时的 ID + 版本检查目标，避免基于过期列表误删记忆。
                if not current or current['version'] != change['version']:
                    raise MemoryConflictError('记忆版本已变化，请刷新')
                documents.remove(current)
            else:
                raise ValueError('未知记忆操作')
        self.documents[owner_id] = documents  # 全部变更成功后才一次性提交。
        return self.list(owner_id)


class KnowledgeProvider:
    def __init__(self) -> None:
        self.documents: dict[str, str] = {}

    def ingest(self, identifier: str, content: str) -> None:
        # 学习版直接用 ID 覆盖保存文档，供 retrieve 的文本包含匹配使用。
        self.documents[identifier] = content

    def retrieve(self, question: str) -> list[dict]:
        # 这是字面子串检索，没有向量索引或大模型推理。
        return [{'id': key, 'content': text} for key, text in self.documents.items() if question in text]


class WebRetrieval:
    """可替换的检索接口；演示不会联网，不将夹具当作真实新闻。"""
    def capabilities(self) -> list[str]:
        return ['web-search', 'url-fetch']

    async def search(self, query: str, limit: int = 3) -> dict:
        # 返回固定资料及引用，演示后台从 search 结果取 URL 再调用 fetch_url。
        citation = {'url': 'https://example.test/study', 'title': '离线演示资料', 'source': 'offline-demo'}
        return {'query': query, 'citations': [citation] if limit else [],
                'content': '这是演示检索结果，不是实时事实。', 'source': 'offline-demo'}

    async def fetch_url(self, url: str) -> dict:
        # 仅允许夹具 URL；read 标记用于在最终引用中表明已读取页面内容。
        if url != 'https://example.test/study':
            raise ValueError('离线模式只提供固定演示页面')
        return {'citations': [{'url': url, 'title': '离线演示资料', 'read': True}],
                'content': 'Python 学习版通过明确的组件边界理解 Agent 工作流。', 'source': 'offline-demo'}
