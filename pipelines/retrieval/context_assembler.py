import tiktoken

def assemble_context(query: str, chunks, token_budget=4000, model="gpt-4o-mini"):
    enc = tiktoken.encoding_for_model(model)
    context = []
    total_tokens = 0
    used = []

    for c in chunks:
        tokens = len(enc.encode(c.content))
        if total_tokens + tokens > token_budget:
            break
        context.append(f"[Source — chunk {c.chunk_id}]\n{c.content}\n")
        total_tokens += tokens
        used.append(c.chunk_id)

    return {
        "context": "\n".join(context),
        "chunks_used": used,
        "total_tokens": total_tokens,
        "sources": [f"chunk {c.chunk_id}" for c in chunks]
    }
