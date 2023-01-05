from src.db import db_module

from . import settings


async def get_db_session():
    db = await db_module.create_session(settings.DATABASE_URI)
    try:
        yield db
    finally:
        db.close()
