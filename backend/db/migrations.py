import asyncpg
import pathlib

async def apply_schema():
    conn = await asyncpg.connect("postgresql://neuroflow:password@postgres:5432/neuroflow")
    schema_path = pathlib.Path(__file__).parent.parent / "infra" / "init" / "001_schema.sql"
    with open(schema_path, "r") as f:
        sql = f.read()
    await conn.execute(sql)
    await conn.close()
