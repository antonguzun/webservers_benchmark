from asyncpg import create_pool
from asyncpg.pool import Pool


async def create_session(uri: str) -> Pool:
    try:
        print("creating asyncpg pool")
        return await create_pool(dsn=uri, max_size=10)
    except Exception as e:
        print(e)
        raise Exception("error during asyncpg pool creation") from e


async def close_session(session: Pool):
    await session.close()