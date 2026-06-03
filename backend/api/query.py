from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
import uuid, asyncio

router = APIRouter()

@router.post("/query")
async def query_endpoint(body: dict):
    run_id = str(uuid.uuid4())
    query = body["query"]
    pipeline_id = body["pipeline_id"]
    stream = body.get("stream", True)

    if stream:
        return {"run_id": run_id}
    else:
        # Run synchronously and return full JSON
        result = await run_pipeline(query, pipeline_id, run_id)
        return result

@router.get("/query/{run_id}/stream")
async def stream_query(run_id: str):
    async def event_generator():
        yield {"data": json.dumps({"type": "retrieval_start"})}
        # retrieval + generation pipeline
        async for event in run_pipeline_stream(run_id):
            yield {"data": json.dumps(event)}
        yield {"data": json.dumps({"type": "done", "run_id": run_id})}

        # keepalive every 15s
        while True:
            await asyncio.sleep(15)
            yield {"data": json.dumps({"type": "keepalive"})}

    return EventSourceResponse(event_generator())
