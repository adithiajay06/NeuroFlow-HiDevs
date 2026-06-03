import asyncio
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage

async def rerank(query: str, candidates, client: NeuroFlowClient):
    async def score_pair(chunk):
        messages = [ChatMessage(role="user", content=f"Rate relevance 0-10. Query: {query}. Passage: {chunk.content}")]
        result = await client.chat(messages, RoutingCriteria(task_type="rag_generation"))
        return float(result.content.strip()), chunk

    scored = await asyncio.gather(*[score_pair(c) for c in candidates[:40]])
    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored]
