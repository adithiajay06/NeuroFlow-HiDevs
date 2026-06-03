def suggest_improvements(pipeline_id, eval_results):
    suggestions = []
    if eval_results["context_precision"] < 0.5:
        suggestions.append("Reduce top_k_after_rerank to improve precision.")
    if eval_results["context_recall"] < 0.5:
        suggestions.append("Increase dense_k to improve recall.")
    return suggestions
