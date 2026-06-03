from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage

async def hyde_embed(query: str, client: NeuroFlowClient):
    # Generate hypothetical answer
    messages = [ChatMessage(role="user", content=f"Write a detailed answer to: {query}")]
    result = await client.chat(messages, RoutingCriteria(task_type="rag_generation"))
    hypo_answer = result.content

    # Embed hypothetical answer instead of raw query
    embedding = await client.embed([hypo_answer], RoutingCriteria(task_type="embedding"))
    return embedding
