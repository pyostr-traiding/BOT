from typing import Union

import aiohttp

from API.other.schema.user import TGUserSchema
from conf.settings import settings


async def get_or_create_user(
        chat_id: str,
        username: str,
):
    """
    Создать или получить пользователя
    """
    payload = {
        "username": username,
        "chat_id": chat_id,
    }
    url = f'{settings.BASE_API_URL}/users/GetOrCreate'
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=url,
                json=payload,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return TGUserSchema(**await resp.json())


async def user_balance(
        chat_id: str,
        decries: bool = False
) -> Union[dict, None]:
    payload = {
        'chat_id': chat_id,
        'decries': decries
    }
    url = f'{settings.BASE_API_URL}/users/balance'
    async with aiohttp.ClientSession() as session:
        async with session.post(
                url=url,
                json=payload,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return await resp.json()


async def user_add_permissions(
        username: str
) -> Union[dict, None]:
    url = f'{settings.BASE_API_URL}/users/addPermission'
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=url,
                params={'username': username},
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return 200
            if resp.status == 404:
                return 404

