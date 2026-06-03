import time, re, json, asyncio
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria
from backend.providers.base import ChatMessage
from .citations import parse_citations

async def generate(query, query_type, context_result, client: NeuroFlowClient, run_id: str, redis):
    prompt = build_prompt(query, query_type, context_result["context"])

    # Log pipeline run before LLM call
    pipeline_run = {
        "run_id": run_id,
        "prompt": prompt,
        "status": "started",
        "start_time": time.time()
    }
    # await db.insert("pipeline_runs", pipeline_run)

    messages = [ChatMessage(role="user", content=prompt)]
    criteria = RoutingCriteria(task_type="rag_generation")

    full_response = ""
    start = time.time()

    async for token in client.stream(messages, criteria):
        full_response += token
        yield {"type": "token", "delta": token}

    latency = (time.time() - start) * 1000
    citations = parse_citations(full_response, context_result)

    # Update pipeline run
    pipeline_run.update({
        "generation": full_response,
        "output_tokens": len(full_response.split()),
        "latency_ms": latency,
        "status": "complete",
        "citations": citations
    })
    # await db.update("pipeline_runs", run_id, pipeline_run)

    # Enqueue evaluation job asynchronously
    await redis.lpush("queue:evaluate", json.dumps({"run_id": run_id}))

    yield {"type": "done", "run_id": run_id, "citations": citations}
