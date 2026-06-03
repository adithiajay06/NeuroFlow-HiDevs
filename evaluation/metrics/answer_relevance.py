async def evaluate_answer_relevance(query: str, answer: str, client) -> float:
    prompt = f"Generate 3-5 questions that this answer could be a response to:\n{answer}"
    res = await client.chat([{"role":"user","content":prompt}], {"task_type":"evaluation"})
    questions = res.content.split("\n")

    q_emb = await client.embed([query], {"task_type":"embedding"})
    gen_emb = await client.embed(questions, {"task_type":"embedding"})

    sims = [cosine_similarity(q_emb, e) for e in gen_emb]
    return sum(sims)/len(sims)
