import json
import asyncio
import aioredis
import time
from opentelemetry import trace

from .extractors import pdf_extractor, docx_extractor, image_extractor, csv_extractor, url_extractor
from .chunker import auto_chunk
from backend.providers.client import NeuroFlowClient
from backend.providers.router import RoutingCriteria

tracer = trace.get_tracer("neuroflow.ingest.worker")

async def process_job(job: dict, client: NeuroFlowClient):
    document_id = job["document_id"]
    file_path = job.get("file_path")
    source_type = job.get("source_type")

    start = time.time()
    pages = []

    # Select extractor
    if source_type == "upload" and file_path.endswith(".pdf"):
        pages = pdf_extractor.extract_pdf(file_path)
    elif source_type == "upload" and file_path.endswith(".docx"):
        pages = docx_extractor.extract_docx(file_path)
    elif source_type == "upload" and file_path.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        pages = image_extractor.extract_image(file_path, client)
    elif source_type == "upload" and file_path.endswith(".csv"):
        pages = csv_extractor.extract_csv(file_path)
    elif source_type == "url":
        pages = await url_extractor.extract_url(job["url"])

    # Chunking
    chunks = auto_chunk(pages, client)

    # Embedding calls
    embedding_calls = 0
    for chunk in chunks:
        await client.embed([chunk], RoutingCriteria(task_type="embedding"))
        embedding_calls += 1

    duration = (time.time() - start) * 1000

    # Observability
    with tracer.start_as_current_span("ingestion.process") as span:
        span.set_attribute("document_id", document_id)
        span.set_attribute("source_type", source_type)
        span.set_attribute("page_count", len(pages))
        span.set_attribute("chunk_count", len(chunks))
        span.set_attribute("embedding_calls", embedding_calls)

    print(json.dumps({
        "event": "ingestion_complete",
        "document_id": document_id,
        "duration_ms": duration,
        "chunks": len(chunks),
        "tokens": sum(len(c.split()) for c in chunks)
    }))

    # Update DB status (pseudo-code)
    # await db.execute("UPDATE documents SET status=?, chunk_count=? WHERE id=?",
    #                  ["complete", len(chunks), document_id])


async def worker_loop():
    redis = aioredis.from_url("redis://localhost", decode_responses=True)
    client = NeuroFlowClient.get_instance("redis://localhost", "OPENAI_KEY", "ANTHROPIC_KEY")

    while True:
        job_data = await redis.brpop("queue:ingest", timeout=5)
        if job_data:
            _, raw = job_data
            job = json.loads(raw)
            try:
                await process_job(job, client)
            except Exception as e:
                print(f"Error processing job {job['document_id']}: {e}")
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(worker_loop())
