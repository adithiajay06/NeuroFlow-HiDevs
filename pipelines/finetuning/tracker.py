import mlflow
from statistics import mean

def start_training_job(job_id, pairs, base_model, min_date, max_date):
    with mlflow.start_run(run_name=f"finetune-{job_id}") as run:
        mlflow.log_params({
            "base_model": base_model,
            "training_pair_count": len(pairs),
            "avg_quality_score": mean([p.get("quality_score",0.85) for p in pairs]),
            "date_range": f"{min_date} to {max_date}"
        })
        mlflow.log_artifact(f"training_data/{job_id}.jsonl")
        return run.info.run_id

def log_training_metrics(job_result):
    mlflow.log_metrics({
        "training_loss": job_result.training_loss,
        "validation_loss": job_result.validation_loss,
        "training_token_count": job_result.trained_tokens
    })
