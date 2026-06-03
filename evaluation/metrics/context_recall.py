async def evaluate_context_precision(query: str, chunks: list[str], answer: str, client) -> float:
    scores = []
    for i, chunk in enumerate(chunks, start=1):
        prompt = f"Was this passage useful in generating the answer? yes/no\nPassage: {chunk}\nAnswer: {answer}"
        res = await client.chat([{"role":"user","content":prompt}], {"task_type":"evaluation"})
        useful = 1 if "yes" in res.content.lower() else 0
        scores.append(useful * (1/i))
    return sum(scores)/sum(1/i for i in range(1,len(chunks)+1))
