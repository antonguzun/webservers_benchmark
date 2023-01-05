from abc import ABC, abstractmethod

from asyncpg.pool import Pool

from .entities import User


class UserRepo(ABC):
    @abstractmethod
    async def get_user_by_id(self, db: Pool, user_id: int) -> User:
        raise NotImplementedError
