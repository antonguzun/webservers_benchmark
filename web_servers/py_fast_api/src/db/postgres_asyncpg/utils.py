from asyncpg import create_pool
from asyncpg.pool import Pool


async def create_session(uri: str) -> Pool:
    try:
        return await create_pool(dsn=uri)
    except Exception as e:
        raise Exception("error during asyncpg pool creation") from e
