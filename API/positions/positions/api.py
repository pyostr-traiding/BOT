from typing import Union

import aiohttp

from API.positions.positions.schema.position import PositionSchema
from conf.settings import settings
from service.utils.responses import ErrorResponse


async def get_position(
    uuid: str
) -> Union[PositionSchema, ErrorResponse]:
    """
    Получить расчет PNK
    """
    url = f'{settings.BASE_API_URL}/position/getPosition'

    params = {
        'uuid': uuid,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=url,
            params=params,
            headers=settings.BASE_HEADERS
        ) as resp:
            if resp.status == 200:
                return PositionSchema(**await resp.json())
            return ErrorResponse(
                status=resp.status,
                text=await resp.text(),
            )

# print(asyncio.run(get_position('e6579469-22ed-478c-a3ed-00f80b4ca0ff')))