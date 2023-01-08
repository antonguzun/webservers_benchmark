from aiomysql import Pool

from ..base import UserAccessModel as BaseUserAccessModel
from ..entities import UpdateUser, User


class UserAccessModel(BaseUserAccessModel):
    __query_get_by_user_id = """
        SELECT user_id, username, email, created_at, updated_at, is_archived 
        FROM users WHERE user_id=%s LIMIT 1;
    """
    __query_update_user = """
        UPDATE users SET username=%s, email=%s, updated_at=NOW() 
        WHERE user_id=%s;
    """

    @classmethod
    async def get_user_by_id(cls, db: Pool, user_id: int) -> User | None:
        async with db.acquire() as conn:
            cur = await conn.cursor()
            params = [user_id]
            result = await cur.execute(cls.__query_get_by_user_id, params)
            result = await cur.fetchone()
            if not result:
                return None
            return User(
                user_id=result[0],
                username=result[1],
                email=result[2],
                created_at=result[3],
                updated_at=result[4],
                is_archived=result[5],
            )

    @classmethod
    async def update_user(cls, db: Pool, user_id: int, data: UpdateUser) -> User:
        async with db.acquire() as conn:
            cur = await conn.cursor()
            params = [data.username, data.email, user_id]
            result = await cur.execute(cls.__query_update_user, params)
            params = [user_id]
            result = await cur.execute(cls.__query_get_by_user_id, params)
            result = await cur.fetchone()
            if not result:
                return None
            return User(
                user_id=result[0],
                username=result[1],
                email=result[2],
                created_at=result[3],
                updated_at=result[4],
                is_archived=result[5],
            )
