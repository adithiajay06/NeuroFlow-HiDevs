import asyncio, json
from pipelines.retrieval.retriever import Retriever

async def evaluate(pipeline, test_set):
    hits, rr_sum = 0, 0
    for test in test_set:
        results = await pipeline.retrieve(test["query"], {}, k=10)
        relevant = test["relevant_chunk_ids"]
        hit = any(r.chunk_id in relevant for r in results)
        if hit: hits += 1
        rank = next((i+1 for i, r in enumerate(results) if r.chunk_id in relevant), None)
        if rank: rr_sum += 1 / rank
    hit_rate = hits / len(test_set)
    mrr = rr_sum / len(test_set)
    with open("evaluation/retrieval_results.json", "w") as f:
        json.dump({"hit_rate": hit_rate, "mrr": mrr}, f)
    return hit_rate, mrr
