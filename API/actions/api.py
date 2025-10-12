from typing import Union

import aiohttp

from API.positions.positions.schema.position import PositionSchema
from conf.settings import settings
from service.utils.responses import ErrorResponse


async def get_general_analiz(
    tg_id: str
) -> bool:
    """
    Запросить общий анализ
    """
    url = f'{settings.BASE_API_URL}/actions/getGeneralAnaliz'

    payload = {
        'action': 'general_analiz',
        'tg_id': tg_id,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url=url,
            json=payload,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return True

