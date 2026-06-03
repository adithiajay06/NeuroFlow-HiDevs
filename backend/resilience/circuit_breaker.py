import time, aioredis

class CircuitOpenError(Exception): pass

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold=5, recovery_timeout=60, half_open_max_calls=3):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.redis = aioredis.from_url("redis://localhost")

    async def __aenter__(self):
        state = await self.redis.get(f"circuit:{self.name}:state") or "closed"
        if state == "open":
            raise CircuitOpenError(f"Circuit {self.name} is open")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            count = int(await self.redis.incr(f"circuit:{self.name}:failure_count"))
            if count >= self.failure_threshold:
                await self.redis.set(f"circuit:{self.name}:state", "open")
                await self.redis.set(f"circuit:{self.name}:opened_at", time.time())
        else:
            await self.redis.set(f"circuit:{self.name}:state", "closed")
            await self.redis.set(f"circuit:{self.name}:failure_count", 0)
