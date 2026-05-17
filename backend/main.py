from fastapi import FastAPI
import asyncpg
import aioredis
import httpx

app = FastAPI()

@app.get("/health")
async def health():
    # Check Postgres
    try:
        conn = await asyncpg.connect("postgresql://neuroflow:password@postgres:5432/neuroflow")
        await conn.close()
        postgres_ok = True
    except:
        postgres_ok = False

    # Check Redis
    try:
        redis = await aioredis.from_url("redis://:password@redis:6379")
        await redis.ping()
        redis_ok = True
    except:
        redis_ok = False

    # Check MLflow
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://mlflow:5000")
            mlflow_ok = r.status_code == 200
    except:
        mlflow_ok = False

    return {"status": "ok", "checks": {"postgres": postgres_ok, "redis": redis_ok, "mlflow": mlflow_ok}}

@app.get("/metrics")
def metrics():
    # Prometheus format example
    return "custom_metric 1\n"

