@router.post("/pipelines/compare")
async def compare_pipelines(body: dict):
    query = body["query"]
    a_id, b_id = body["pipeline_a_id"], body["pipeline_b_id"]

    results = await asyncio.gather(
        run_pipeline(query, a_id),
        run_pipeline(query, b_id)
    )

    return {
        "query": query,
        "pipeline_a": results[0],
        "pipeline_b": results[1]
    }
