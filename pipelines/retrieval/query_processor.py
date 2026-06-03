from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage

async def expand_query(query: str, client: NeuroFlowClient) -> list[str]:
    messages = [ChatMessage(role="user", content=f"Generate 3 alternative phrasings for: {query}")]
    result = await client.chat(messages, RoutingCriteria(task_type="rag_generation"))
    return [query] + result.content.split("\n")

def extract_metadata_filters(query: str) -> dict:
    filters = {}
    if "2023" in query:
        filters["year"] = 2023
    if "climate" in query.lower():
        filters["topic"] = "climate"
    return filters

def classify_query(query: str) -> str:
    if "compare" in query.lower():
        return "comparative"
    elif "how" in query.lower() or "process" in query.lower():
        return "procedural"
    elif "why" in query.lower() or "analysis" in query.lower():
        return "analytical"
    else:
        return "factual"
