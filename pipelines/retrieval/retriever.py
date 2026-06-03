import asyncio
from typing import List
from .fusion import reciprocal_rank_fusion

class RetrievalResult:
    def __init__(self, chunk_id, content, score):
        self.chunk_id = chunk_id
        self.content = content
        self.score = score

class Retriever:
    def __init__(self, db):
        self.db = db

    async def _dense_retrieval(self, query: str, k: int) -> List[RetrievalResult]:
        # pgvector HNSW search
        rows = await self.db.fetch_all(
            "SELECT id, content, embedding <=> $1 AS score FROM chunks ORDER BY score LIMIT $2",
            [query, k]
        )
        return [RetrievalResult(r["id"], r["content"], r["score"]) for r in rows]

    async def _sparse_retrieval(self, query: str, k: int) -> List[RetrievalResult]:
        rows = await self.db.fetch_all(
            "SELECT id, content, ts_rank_cd(to_tsvector('english', content), plainto_tsquery($1)) AS score "
            "FROM chunks WHERE to_tsvector('english', content) @@ plainto_tsquery($1) "
            "ORDER BY score DESC LIMIT $2",
            [query, k]
        )
        return [RetrievalResult(r["id"], r["content"], r["score"]) for r in rows]

    async def _metadata_retrieval(self, filters: dict, query: str, k: int) -> List[RetrievalResult]:
        if not filters:
            return []
        rows = await self.db.fetch_all(
            "SELECT id, content, embedding <=> $2 AS score FROM chunks WHERE metadata @> $1::jsonb ORDER BY score LIMIT $3",
            [filters, query, k]
        )
        return [RetrievalResult(r["id"], r["content"], r["score"]) for r in rows]

    async def retrieve(self, query: str, filters: dict, k: int = 20) -> List[RetrievalResult]:
        results = await asyncio.gather(
            self._dense_retrieval(query, k),
            self._sparse_retrieval(query, k),
            self._metadata_retrieval(filters, query, k)
        )
        return reciprocal_rank_fusion(results)
