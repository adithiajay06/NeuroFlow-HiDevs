import re, json

PII_REGEX = re.compile(r"[\w\.-]+@[\w\.-]+|\+?\d[\d\s-]{7,}")

async def extract_training_pairs(db, job_id: str):
    rows = await db.fetch_all("""
        SELECT * FROM training_pairs
        WHERE quality_score >= 0.82
        AND included_in_job IS NULL
        AND (user_rating IS NULL OR user_rating >= 4)
    """)

    pairs = []
    for r in rows:
        # Validation
        if len(r["answer"].split()) < 50 or len(r["answer"].split()) > 2000:
            continue
        if "[Source" not in r["answer"]:
            continue
        if PII_REGEX.search(r["query"]):
            continue

        # Format JSONL
        msg = {
            "messages": [
                {"role": "system", "content": "You are a precise research assistant..."},
                {"role": "user", "content": f"[Context]\n{r['context']}\n[Question]\n{r['query']}"},
                {"role": "assistant", "content": r["answer"]}
            ]
        }
        pairs.append(msg)

    path = f"training_data/{job_id}.jsonl"
    with open(path, "w") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    return path, pairs
