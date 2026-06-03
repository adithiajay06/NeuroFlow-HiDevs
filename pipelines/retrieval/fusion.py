def reciprocal_rank_fusion(result_lists, k=60):
    scores = {}
    for result_list in result_lists:
        for rank, r in enumerate(result_list):
            scores[r.chunk_id] = scores.get(r.chunk_id, 0) + 1 / (k + rank + 1)
    fused = [r for lst in result_lists for r in lst]
    fused.sort(key=lambda r: scores.get(r.chunk_id, 0), reverse=True)
    return fused
