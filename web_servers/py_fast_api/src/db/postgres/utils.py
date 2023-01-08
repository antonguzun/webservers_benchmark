from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

async def create_session(uri: str):
    engine = create_async_engine(uri)
    return async_sessionmaker(engine, expire_on_commit=False)
