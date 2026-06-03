async def acquire_token(bucket_key: str, capacity: int, refill_rate: int):
    redis = aioredis.from_url("redis://localhost")
    tokens = await redis.get(bucket_key)
    if tokens is None:
        await redis.set(bucket_key, capacity)
        tokens = capacity
    if int(tokens) > 0:
        await redis.decr(bucket_key)
        return True
    return False
