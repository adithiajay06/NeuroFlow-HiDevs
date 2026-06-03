async def check_queue_depth(redis):
    depth = await redis.llen("queue:ingest")
    if depth > 100:
        return {"status":503,"error":"ingestion_queue_full","queue_depth":depth,"retry_after":30}
    elif depth > 50:
        return {"status":202,"warning":"high_queue_depth","estimated_wait_minutes":depth//10}
    return {"status":200}
