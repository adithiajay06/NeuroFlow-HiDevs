async def evaluate_faithfulness(query: str, answer: str, context: str, client) -> float:
    if not context.strip() and answer.strip():
        return 0.0

    # Extract claims
    claims_prompt = f"List all factual statements in JSON array from: {answer}"
    claims = await client.chat([{"role":"user","content":claims_prompt}], {"task_type":"evaluation"})
    claims_list = claims.content.split("\n")

    supported = 0
    for claim in claims_list:
        check_prompt = f"Is this claim supported by the context? Claim: {claim}\nContext: {context}\nAnswer yes/no/partial"
        res = await client.chat([{"role":"user","content":check_prompt}], {"task_type":"evaluation"})
        if "yes" in res.content.lower(): supported += 1
        elif "partial" in res.content.lower(): supported += 0.5

    return supported / max(len(claims_list), 1)
