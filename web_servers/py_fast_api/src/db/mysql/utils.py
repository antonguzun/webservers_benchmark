from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = None


async def create_session(uri: str):
    global engine
    engine = create_async_engine(uri)
    return async_sessionmaker(engine, expire_on_commit=False)


async def close_session(db: async_sessionmaker[AsyncSession]):
    global engine
    await engine.dispose()
