from typing import Union

import aiohttp
from httplib2.auth import params

from API.positions.positions.schema.position import PositionSchema
from API.settings.ban.schema.ban import ListSettingsBanSchema, SettingsBanSchema
from conf.settings import settings
from service.utils.responses import ErrorResponse



async def get_settings_ban_list() -> Union[ListSettingsBanSchema, ErrorResponse]:
    """
    Получить список всех значений настроек блокировок
    """
    url = f'{settings.BASE_API_URL}/settings/ListSettingsBan'

    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=url,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return ListSettingsBanSchema(**await resp.json())
            return ErrorResponse(
                status=resp.status,
                text=await resp.text(),
            )


async def get_settings_ban(
        code: str,
        key: str,
) -> Union[SettingsBanSchema, ErrorResponse]:
    """
    Получить данные о блокировке
    """
    url = f'{settings.BASE_API_URL}/settings/settingsBan'
    params = {
        'code': code,
        'key': key,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=url,
            params=params,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return SettingsBanSchema(**await resp.json())
            return ErrorResponse(
                status=resp.status,
                text=await resp.text(),
            )

async def update_settings_ban(
        code: str,
        key: str,
        value: int
) -> Union[SettingsBanSchema, ErrorResponse]:
    """
    Обновить данные
    """
    url = f'{settings.BASE_API_URL}/settings/settingsBan'
    payload = {
          "code": code,
          "key": key,
          "value": value
    }
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url=url,
            json=payload,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return SettingsBanSchema(**await resp.json())
            return ErrorResponse(
                status=resp.status,
                text=await resp.text(),
            )

