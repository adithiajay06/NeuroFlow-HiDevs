
import hashlib
import json
import aiofiles
import aioredis
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from opentelemetry import trace

router = APIRouter()
tracer = trace.get_tracer("neuroflow.ingest")

redis = aioredis.from_url("redis://localhost", decode_responses=True)

@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    if file.size and file.size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 100MB)")

    # Read file bytes
    async with aiofiles.open(f"/tmp/{file.filename}", "wb") as f:
        content = await file.read()
        await f.write(content)

    # Deduplication via sha256
    content_hash = hashlib.sha256(content).hexdigest()
    # Check DB for existing hash (pseudo-code, replace with actual DB query)
    existing_doc = None  # await db.fetch_one("SELECT id FROM documents WHERE content_hash=?", [content_hash])
    if existing_doc:
        return JSONResponse({"document_id": existing_doc["id"], "status": "duplicate", "duplicate": True})

    # Insert new document row (pseudo-code)
    document_id = "doc_" + content_hash[:8]
    # await db.execute("INSERT INTO documents (id, content_hash, status) VALUES (?, ?, ?)", [document_id, content_hash, "queued"])

    # Enqueue job
    job = {"document_id": document_id, "file_path": f"/tmp/{file.filename}", "source_type": "upload"}
    await redis.lpush("queue:ingest", json.dumps(job))

    return JSONResponse({"document_id": document_id, "status": "queued", "duplicate": False})


@router.get("/documents/{document_id}")
async def get_document_status(document_id: str):
    # Pseudo-code: fetch from DB
    doc = {"id": document_id, "status": "processing", "chunk_count": 12, "metadata": {"source_type": "upload"}}
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return JSONResponse(doc)
