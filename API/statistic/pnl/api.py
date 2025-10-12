from typing import Union

import aiohttp

from API.statistic.schema.pnl import PNLSchema
from conf.settings import settings
from service.utils.responses import ErrorResponse


async def get_pnl(
    PNL_period: str
) -> Union[PNLSchema, ErrorResponse]:
    """
    Получить расчет PNK
    """
    url = f'{settings.BASE_API_URL}/statistic/pnl'
    async with aiohttp.ClientSession() as session:
        async with session.get(
                url=url,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return PNLSchema(**await resp.json())
            return ErrorResponse(
                status=resp.status,
                text=await resp.text(),
            )