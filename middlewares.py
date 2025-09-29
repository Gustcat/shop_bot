from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, Update
from sqlalchemy import select

from db import User, async_session


class UserMiddleware(BaseMiddleware):

    async def __call__(self, handler, event: Message | CallbackQuery, data: dict):
        if isinstance(event, Update):
            if event.message and event.message.from_user:
                telegram_id = event.message.from_user.id
            elif event.callback_query and event.callback_query.from_user:
                telegram_id = event.callback_query.from_user.id
        elif isinstance(event, (Message, CallbackQuery)):
            if event.from_user:
                telegram_id = event.from_user.id
        else:
            data["user"] = None
            return await handler(event, data)
        async with async_session() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()
            data["user"] = user

        return await handler(event, data)
