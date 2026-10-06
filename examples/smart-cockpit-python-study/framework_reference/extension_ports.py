"""可运行的记忆/知识/网页能力；默认数据在内存，网页内容是离线夹具。"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4


class MemoryConflictError(ValueError):
    pass


class MemoryProvider:
    def __init__(self) -> None:
        self.documents: dict[str, list[dict]] = {}

    def list(self, owner_id: str) -> list[dict]:
        return deepcopy(self.documents.get(owner_id, []))

    def apply(self, owner_id: str, changes: list[dict]) -> list[dict]:
        documents = self.list(owner_id)
        for change in changes:
            if change['operation'] == 'add':
                documents.append({'id': uuid4().hex, 'text': change['text'], 'version': 1})
            elif change['operation'] == 'remove':
                current = next((d for d in documents if d['id'] == change['id']), None)
                if not current or current['version'] != change['version']:
                    raise MemoryConflictError('记忆版本已变化，请刷新')
                documents.remove(current)
            else:
                raise ValueError('未知记忆操作')
        self.documents[owner_id] = documents
        return self.list(owner_id)


class KnowledgeProvider:
    def __init__(self) -> None:
        self.documents: dict[str, str] = {}

    def ingest(self, identifier: str, content: str) -> None:
        self.documents[identifier] = content

    def retrieve(self, question: str) -> list[dict]:
        return [{'id': key, 'content': text} for key, text in self.documents.items() if question in text]


class WebRetrieval:
    """可替换的检索接口；演示不会联网，不将夹具当作真实新闻。"""
    def capabilities(self) -> list[str]:
        return ['web-search', 'url-fetch']

    async def search(self, query: str, limit: int = 3) -> dict:
        citation = {'url': 'https://example.test/study', 'title': '离线演示资料', 'source': 'offline-demo'}
        return {'query': query, 'citations': [citation] if limit else [],
                'content': '这是演示检索结果，不是实时事实。', 'source': 'offline-demo'}

    async def fetch_url(self, url: str) -> dict:
        if url != 'https://example.test/study':
            raise ValueError('离线模式只提供固定演示页面')
        return {'citations': [{'url': url, 'title': '离线演示资料', 'read': True}],
                'content': 'Python 学习版通过明确的组件边界理解 Agent 工作流。', 'source': 'offline-demo'}
