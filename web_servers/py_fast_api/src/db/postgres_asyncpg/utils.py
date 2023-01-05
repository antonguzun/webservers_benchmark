from asyncpg import create_pool
from asyncpg.pool import Pool


async def create_session(uri: str) -> Pool:
    return await create_pool(uri)
