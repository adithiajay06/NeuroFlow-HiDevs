import asyncpg
from typing import Optional

pool: Optional[asyncpg.pool.Pool] = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn="postgresql://neuroflow:password@postgres:5432/neuroflow",
        min_size=1,
        max_size=5
    )

async def close_pool():
    global pool
    if pool:
        await pool.close()
