from sqlalchemy import Boolean, DateTime, Integer, String, Text, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column

from ..base import UserAccessModel as BaseUserAccessModel
from ..entities import UpdateUser, User


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    user_id = mapped_column(Integer, primary_key=True)
    username = mapped_column(Text, nullable=False)
    email = mapped_column(String, nullable=True)
    created_at = mapped_column(DateTime, nullable=False)
    updated_at = mapped_column(DateTime, nullable=False)
    is_archived = mapped_column(Boolean, nullable=False, default=False)


class UserAccessModel(BaseUserAccessModel):
    @classmethod
    async def get_user_by_id(cls, db: async_sessionmaker[AsyncSession], user_id: int) -> User | None:
        async with db() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id).limit(1)
            result = await session.execute(stmt)
            result = result.scalars().first()
            await session.commit()
            if not result:
                return None
            return User(
                user_id=result.user_id,
                username=result.username,
                email=result.email,
                created_at=result.created_at,
                updated_at=result.updated_at,
                is_archived=result.is_archived,
            )

    @classmethod
    async def update_user(cls, db: async_sessionmaker[AsyncSession], user_id: int, data: UpdateUser) -> User:
        async with db() as session:
            stmt = select(UserModel).where(UserModel.user_id == user_id).limit(1)
            result = await session.execute(stmt)
            result = result.scalars().one()
            if not result:
                return None
            result.username = data.username
            result.email = data.email
            await session.commit()
            return User(
                user_id=result.user_id,
                username=result.username,
                email=result.email,
                created_at=result.created_at,
                updated_at=result.updated_at,
                is_archived=result.is_archived,
            )
