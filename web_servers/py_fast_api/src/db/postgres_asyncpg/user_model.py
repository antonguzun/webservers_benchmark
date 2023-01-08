from asyncpg.pool import Pool

from ..base import UserAccessModel as BaseUserAccessModel
from ..entities import UpdateUser, User


class UserAccessModel(BaseUserAccessModel):
    __query_get_by_user_id = """
        SELECT user_id, username, email, created_at, updated_at, is_archived 
        FROM users WHERE user_id=$1 LIMIT 1
    """
    __query_update_user = """
        UPDATE users SET username=$2, email=$3, updated_at=NOW() 
        WHERE user_id=$1 
        RETURNING user_id, username, email, created_at, updated_at, is_archived 
    """

    @classmethod
    async def get_user_by_id(cls, db: Pool, user_id: int) -> User | None:
        result = await db.fetchrow(cls.__query_get_by_user_id, user_id)
        if not result:
            return None
        return User(**result)

    @classmethod
    async def update_user(cls, db: Pool, user_id: int, data: UpdateUser) -> User:
        result = await db.fetchrow(cls.__query_update_user, user_id, data.username, data.email)
        if not result:
            return None
        return User(**result)
