from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from db import User


async def create_user(session: AsyncSession, tg_user: TelegramObject) -> User:
    user = User(
        telegram_id=tg_user.id,
        username=tg_user.username,
        full_name=f"{tg_user.first_name} {tg_user.last_name or ''}".strip(),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user
