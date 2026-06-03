async def evaluate_context_recall(query: str, chunks: list[str], answer: str, client) -> float:
    sentences = answer.split(".")
    attributable = 0
    for s in sentences:
        prompt = f"Can this sentence be attributed to the provided context?\nSentence: {s}\nContext: {chunks}"
        res = await client.chat([{"role":"user","content":prompt}], {"task_type":"evaluation"})
        if "yes" in res.content.lower(): attributable += 1
    return attributable / max(len(sentences),1)
