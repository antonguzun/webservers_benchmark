from asyncpg.pool import Pool

from ..base import UserRepo as BaseUserRepo
from ..entities import User


class UserRepo(BaseUserRepo):
    __query_get_by_user_id = """
        SELECT user_id, username, email, meta_data, created_at, updated_at, is_archived 
        FROM users WHERE id=5 LIMIT 1
    """
    @classmethod
    async def get_user_by_id(cls, db: Pool, user_id: int) -> User:
        result = await db.fetch(cls.__query_get_by_user_id, user_id)
        return User(**result)
