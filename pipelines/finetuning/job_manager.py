from openai import AsyncOpenAI
import asyncio

async def submit_finetune_job(jsonl_path: str, base_model: str):
    client = AsyncOpenAI()
    file_resp = await client.files.create(file=open(jsonl_path, "rb"), purpose="fine-tune")
    job = await client.fine_tuning.jobs.create(training_file=file_resp.id, model=base_model)
    return job.id

async def poll_job(job_id, db, router, run_id):
    client = AsyncOpenAI()
    while True:
        job = await client.fine_tuning.jobs.retrieve(job_id)
        if job.status == "succeeded":
            await db.execute("UPDATE finetune_jobs SET status='succeeded', provider_job_id=? WHERE id=?", [job.id, job_id])
            router.register_model(job.id, task_type="rag_generation", prefer_fine_tuned=True)
            mlflow.register_model(f"runs:/{run_id}/model", f"neuroflow-finetune-{job_id}")
            break
        await asyncio.sleep(60)
