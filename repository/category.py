from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from asyncpg import UniqueViolationError
from sqlalchemy.ext.asyncio import AsyncSession

from db import Category


async def get_or_create_category(session: AsyncSession, name: str) -> Category:
    """Получает категорию по имени или создаёт её, если не существует."""
    category = Category(name=name)
    session.add(category)
    try:
        await session.commit()
        return category
    except IntegrityError as e:
        await session.rollback()
        if isinstance(e.orig, UniqueViolationError):
            result = await session.execute(
                select(Category).where(Category.name == name)
            )
            return result.scalar_one()
        else:
            raise
