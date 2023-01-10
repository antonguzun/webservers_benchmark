import aiomysql
import asyncio


async def create_session(uri: str) -> aiomysql.Pool:
    try:
        loop = asyncio.get_event_loop()
        print("creating aiomysql pool")
        user, password, host, port, db = uri.split(";")
        return await aiomysql.create_pool(
            host=host, port=int(port), user=user, password=password, db=db, loop=loop, autocommit=True, maxsize=10
        )
    except Exception as e:
        print(e)
        raise Exception("error during aiomysql pool creation") from e


async def close_session(pool: aiomysql.Pool):
    pool.close()
    await pool.wait_closed()

