from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy import select

from db import UserRole, User, async_session


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message | CallbackQuery, data: dict):
        id = 0
        if isinstance(event, Update):
            if event.message:
                id = event.message.from_user.id
            elif event.callback_query:
                id = event.callback_query.from_user.id
            else:
                return await handler(event, data)
        else:
            id = event.from_user.id
        async with async_session() as session:
            res = await session.execute(select(User).where(User.telegram_id == id))
            user = res.scalars().one_or_none()
            data["is_admin"] = bool(user and user.role == UserRole.ADMIN)
        print("&&&&&&&&&")
        return await handler(event, data)
