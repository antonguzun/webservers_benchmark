from abc import ABC, abstractmethod

from asyncpg.pool import Pool

from .entities import User, UpdateUser


class UserAccessModel(ABC):
    @abstractmethod
    async def get_user_by_id(self, db: Pool, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    async def update_user(self, db: Pool, user_id: int, data=UpdateUser) -> User:
        raise NotImplementedError
