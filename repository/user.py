from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import User


async def get_or_create_user(session: AsyncSession, tg_user):
    stmt = select(User).where(User.telegram_id == tg_user.id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            telegram_id=tg_user.id,
            username=tg_user.username,
            full_name=f"{tg_user.first_name} {tg_user.last_name or ''}".strip(),
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
