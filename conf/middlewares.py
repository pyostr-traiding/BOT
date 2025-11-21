import time
from typing import Dict, Any, Awaitable, Callable
from aiogram import types

from API.other.user import get_or_create_user
from conf.base import USER_CACHE
from conf.conf import dp, client
from conf.connect import command_connect


commands = [
    '/receipt',
    '/search',
    '/start',
    '/extract',
    '/add',
]

REFRESH_INTERVAL = 5  # секунд

@dp.update.outer_middleware()
async def auth_middleware(
        handler: Callable[[types.Update, Dict[str, Any]], Awaitable[Any]],
        event: types.Update,
        data: Dict[str, Any]
) -> Any:
    """
    Авторизуем пользователя.
    Проверяем что пользователь авторизован и токен активен.
    Или авторизуем пользователя
    """
    user_data: types.User = data['event_from_user']
    chat_id = str(user_data.id)

    now = time.time()
    cache_entry = USER_CACHE.get(chat_id)

    # Проверяем, есть ли запись и не устарела ли она
    if not cache_entry or now - cache_entry["timestamp"] > REFRESH_INTERVAL:
        user = await get_or_create_user(
            chat_id=chat_id,
            username=user_data.username,
        )
        if user:
            USER_CACHE[chat_id] = {"user": user, "timestamp": now}
        else:
            return await client.send_message(
                chat_id=user_data.id,
                text='Ошибка авторизация!'
            )

    # В data кладем актуальные данные пользователя
    data["auth_user"] = USER_CACHE[chat_id]["user"]

    if event.message and event.message.text in commands:
        return await command_connect(
            message=event.message,
            state=data['state'],
            auth_user=USER_CACHE[chat_id]["user"]
        )

    return await handler(event, data)
