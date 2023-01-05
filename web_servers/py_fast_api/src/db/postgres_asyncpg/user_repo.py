from asyncpg.pool import Pool

from ..base import UserRepo as BaseUserRepo
from ..entities import User


class UserRepo(BaseUserRepo):
    __query_get_by_user_id = """
        SELECT user_id, username, email, metadata, created_at, updated_at, is_archived 
        FROM users WHERE user_id=$1 LIMIT 1
    """

    @classmethod
    async def get_user_by_id(cls, db: Pool, user_id: int) -> User | None:
        result = await db.fetchrow(cls.__query_get_by_user_id, user_id)
        if not result:
            return None
        return User(**result)
