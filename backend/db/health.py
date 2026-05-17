import asyncpg
import aioredis

async def check_postgres():
    try:
        conn = await asyncpg.connect("postgresql://neuroflow:password@postgres:5432/neuroflow")
        await conn.close()
        return True
    except:
        return False

async def check_redis():
    try:
        redis = await aioredis.from_url("redis://:password@redis:6379")
        await redis.ping()
        return True
    except:
        return False
